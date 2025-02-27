'''主要用于清洗声学语料数据集，但如果改改应该也能用于语言模型的数据集清洗'''
from util.mapmap import PinyinMapper,ChsMapper
import os
import re
import json

re_root_path = re.compile("G[0-9]{4}")
re_en_num = re.compile("[a-zA-Z0-9]")
re_sign = re.compile("\.\?？。、“”\"':：，,<>《》（）\(\)！")

class Cleaner():
    '''
    用于清洗和归一化数据集的，主要包括在每个音频下创建相应的同名标签文件，并将标签文件没有汉语的用pinyin库添加拼音

        先生成后清洗
            先不管汉字是否在字典中，在对应的音频文件下生成相应的汉字和拼音（如果没有的话），同时在根目录下生成统计字典。
            随后再根据标签中数字、字母是否存在等进行删除等操作
    '''
    def __init__(self,path,strip_tone = False):
        assert os.path.exists(path), "path not exists!"
        self.path = path
        self.strip_tone = strip_tone
        self.pymap = PinyinMapper()
        self.chs_map = ChsMapper()
    def delete_number_file(self):
        pass

    def gene_label(self):
        '''生成标签，同时统计词频和拼音频率，在根目录下生成dataset_dict_chs.txt和dataset_dict_py.txt'''
        pass

    def check_chs_line_aval(self,line:str):
        '''
        检查该行中的汉字是否出现在字典中，是否有数字，字母，标点符号

        :param line:
        :return: 如果存在未出现在字典中的汉字，或存在字母，则返回False，对应标注应该不能生成
                否则，返回将阿拉伯数字替换为汉字，将标点符号去除后的字符串（无换行符）
        '''
        # TODO

    def count_label(self,line):
        '''统计字频汉字要求字符串，拼音要求list'''
        res = {}
        for i in line:
            num = res.setdefault(i,0)
            res[i] = num+1

        return res

    def merge_count_label(self,res:dict,all_res = None):
        if all_res is None:
            all_res = {}
        for k,v in res.items():
            num = all_res.setdefault(k,0)
            all_res[k] = num+v

        return all_res

    def _write_count_result(self,chs_dict:dict,py_dict:dict):
        chs_dict_path = os.path.join(self.path,f"{self.__class__.__name__}_chs_dict.dict")
        py_dict_path = os.path.join(self.path,f"{self.__class__.__name__}_py_dict.dict")
        with open(chs_dict_path,"w",encoding="utf-8") as w:
            for k,v in chs_dict.items():
                w.write(f"{k}:{v}\n")

        with open(py_dict_path,"w",encoding="utf-8") as w:
            for k,v in py_dict.items():
                w.write(f"{k}:{v}\n")

        print(f"[info*] Write py and chs dict in {self.path}.")

class Thchs30(Cleaner):
    def load_trn_fs(self):
        path = os.path.join(self.path, "data")
        fs = os.listdir(path)
        fs = [os.path.join(path, i) for i in fs]
        return [i for i in fs if i.endswith(".trn")]

    def create_dataset_dict(self):
        '''确保目录下存在汉字和拼音'''
        fs = self.load_trn_fs()
        for f in fs:
            with open(f,encoding="utf-8") as f:
                f.readline()

    def delete_number_file(self):
        fs = self.load_trn_fs()

        for i in fs:
            with open(i,encoding="utf-8") as f:
                line = f.readline().strip()

            if re.search(re_en_num, line) is not None:
                print(f"file {i} have alpha or number, deleted.")
                wavf, _ = os.path.splitext(i)
                os.remove(i)
                os.remove(wavf)

    def gene_label(self):
        '''
        因为thchs 数据集本身标注了拼音，因此这里只生成npy文件
        :param path:
        :param filtermuti:
        :return:
        '''
        # print("Thchs30 dataset has no need to be create pinyin, .\n")
        fs = self.load_trn_fs()
        chs_all_dict = {}
        py_all_dict = {}
        for i,f in enumerate(fs):
            print(f"\rEnumerate in {i},f={f}.",end="\0",flush=True)
            with open(f,encoding="utf-8") as f:
                line = f.readline().strip()
                pyline = f.readline().strip().split(" ")
                chs_dict = self.count_label(line)
                chs_all_dict = self.merge_count_label(chs_dict,chs_all_dict)

                py_dict = self.count_label(pyline)
                py_all_dict = self.merge_count_label(py_dict,py_all_dict)

        self._write_count_result(chs_all_dict,py_all_dict)

class Z200(Cleaner):
    # @staticmethod
    def clean(self):
        '''
        Aidatatang_200zh数据集
        传入包含G0002/G0003...的路径
        :param path:
        :return:
        '''
        self.delete_number_file()

    def load_txt_fs(self):
        root = os.listdir(self.path)
        root = [os.path.join(self.path, i) for i in root if re.search(re_root_path, i) is not None]
        root = [os.path.join(i, "session01/") for i in root]  # 获取每个session01所在的路径

        all_txtfs = []  # 存储了每个txt文件的路径
        for dir in root:
            if os.path.exists(dir):
                fs = os.listdir(dir)
                fs = [os.path.join(dir, i) for i in fs if i.endswith(".txt")]
                all_txtfs.extend(fs)
            else:
                print(f"{dir} not exists, please check it.")

        return all_txtfs

    def delete_number_file(self):
        '''
        删除含有字母或数字的文件
        :param path:
        :return:
        '''
        all_txtfs = self.load_txt_fs()

        for sf in all_txtfs:
            with open(sf, encoding="utf-8") as f, open("log.txt", "w") as log:
                line = f.readline().strip()

            if re.search(re_en_num, line) is not None:
                print(f"file {sf} have alpha or number, deleted.")
                fpre, _ = os.path.splitext(sf)
                os.remove(f"{fpre}.txt")
                os.remove(f"{fpre}.wav")
                os.remove(f"{fpre}.metadata")

    def gene_label(self):
        '''
        z200数据集中只有汉字，没有拼音数据，该方法对其标注的txt添加拼音数据，同时，可以生成相应的npy文件，加快读取速度
        :param path: z200的根目录
        :param filtermuti: 过滤多音字，如果句子中存在多音字，则忽略
        :param genenpy: 生成npy文件，对每类拼音进行标号，生成相应的id序列，以同名npy文件存放到相同路径下
        :param debug: 输出处理序列
        :return:
        '''
        all_txtfs = self.load_txt_fs()

        chs_all_dict = {}
        py_all_dict = {}

        for i,sf in enumerate(all_txtfs):
            print(f"\r{i},{sf}.",end="\0",flush=True)

            with open(sf, encoding="utf-8") as f, open("log.txt", "w") as log:
                line = f.readline().strip()
                pyline = self.pymap.sent2pylist(line,False)

                chs_dict = self.count_label(line)
                py_dict = self.count_label(pyline)
                chs_all_dict = self.merge_count_label(chs_dict,chs_all_dict)
                py_all_dict = self.merge_count_label(py_dict,py_all_dict)

            with open(sf, "w", encoding="utf-8") as f:
                f.write(f"{line}\n")
                f.write(f"{' '.join(pyline)}\n")

        print("z200 finished.")
        self._write_count_result(chs_all_dict,py_all_dict)

class AiShell(Cleaner):
    def clean(self):
        self.gene_pinyin()

    '''AiShell中存在一些没有标注的音频，在生成的时候会被删除'''
    def gene_label(self):
        label_file = os.path.join(self.path,"transcript/aishell_transcript_v0.8.txt")
        assert os.path.exists(label_file),"file 'aishell_transcript_v0.8.txt' not exists, please check dir ./transcript/ ! "
        file_label_map = {}
        with open(label_file,encoding="utf-8") as f:
            for line in f:
                file,label = line.split(" ",maxsplit=1)

                fpre,_ = os.path.splitext(file)
                file_label_map[fpre] = label.strip()

        train_root = os.path.join(self.path,"wav/train")
        test_root = os.path.join(self.path,"wav/test")
        dev_root = os.path.join(self.path,"wav/dev")
        # print(file_label_map)
        i = 0

        chs_all_dict = {}
        py_all_dict = {}
        for fs in [train_root,test_root,dev_root]: #每一个目录
            fs = self._get_sub_wavs(fs)
            for f in fs: # 每一个wav文件
                print(f"\r{i},{f}",end="\0",flush=True)
                i+=1
                path,fname = os.path.split(f)
                fpre,ext = os.path.splitext(fname)

                pyfile = os.path.join(path,f"{fpre}.txt")

                line = file_label_map.get(fpre,None)
                if line is not None:
                    with open(pyfile,"w",encoding="utf-8") as w:
                        line = file_label_map[fpre]
                        pyline = self.pymap.sent2pylist(line,to_str=False)

                        chs_dict = self.count_label(line)
                        py_dict = self.count_label(pyline)
                        chs_all_dict = self.merge_count_label(chs_dict,chs_all_dict)
                        py_all_dict = self.merge_count_label(py_dict,py_all_dict)

                        w.write(f"{line}\n")
                        w.write(f"{' '.join(pyline)}\n")


                else:
                    os.remove(f)
                    print(f"{f} not have label, delete it.")

        self._write_count_result(chs_all_dict,py_all_dict)
        print("Aishell finished.\n")

    def _get_sub_wavs(self,path):
        '''
        接收 ./train/  ./dev/ ./test ,返回相应路径下所有的wav文件
        :param path:
        :return:
        '''
        s_fs = os.listdir(path)
        fs = []
        for f in s_fs:
            s_path = os.path.join(path,f)
            wavfs = os.listdir(s_path)
            wavfs = [os.path.join(s_path,wavf) for wavf in wavfs]
            fs.extend(wavfs)

        fs = [f for f in fs if f.endswith(".wav")] # 过滤审查

        return fs

class ST_CMDS(Cleaner):
    def clean(self):
        '''
        ST-CMDS数据集
        传入包含*.wav/*.txt/*.metadata的路径
        :param path:
        :return:
        '''
        self.gene_pinyin()

    def gene_label(self):
        fs = os.listdir(self.path)
        fs = [os.path.join(self.path,f) for f in fs if f.endswith(".txt")]

        chs_all_dict = {}
        py_all_dict = {}
        for i,f in enumerate(fs):
            print(f"\r{i},{f}.",end="\0",flush=True)
            line = None
            with open(f,encoding="utf-8") as ft: # 打开txt文件读取汉字标注
                line = ft.readline().strip()

            if len(line) > 0:
                pyline = self.pymap.sent2pylist(line) # 转化为拼音

                with open(f,"w",encoding="utf-8") as w: # 写拼音到第二行
                    chs_dict = self.count_label(line)
                    py_dict = self.count_label(pyline)
                    chs_all_dict = self.merge_count_label(chs_dict, chs_all_dict)
                    py_all_dict = self.merge_count_label(py_dict, py_all_dict)

                    w.write(f"{line}\n")
                    w.write(f"{pyline}\n")

        self._write_count_result(chs_all_dict,py_all_dict)
        print(f"ST_CMDS finished.\n")

class Primewords(Cleaner):
    def clean(self):
        '''
        Primewords Chinese Corpus Set 1数据集
        传入包含audio_files/set1_transcript.json 的路径
        :param path:
        :return:
        '''
        self.gene_pinyin()

    def gene_label(self):
        import json
        json_path = os.path.join(self.path,"set1_transcript.json")
        assert os.path.exists(json_path),"set1_transcript.json not exists!"

        jdict = None
        with open(json_path,encoding="utf-8") as f:
            jdict = json.load(f)

        file_label_map = {}
        for sample in jdict:
            file_label_map[sample["file"]] = sample["text"] # 格式 ： "632b4316-d806-448a-b549-650d7e233b80.wav" : "总共有三十支球队 分为东部联盟 西部联盟"

        '''获取每个wav文件'''
        audio_root_dir = os.path.join(self.path,"audio_files") # ./audio_files/
        f0 = os.listdir(audio_root_dir) # 从0-f 的16个目录
        f0 = [os.path.join(audio_root_dir,f) for f in f0]

        ff00 = []  # 包含所有00-ff的文件夹路径
        for f in f0:
            subff = os.listdir(f) # 列出00-ff几个文件夹
            subff = [os.path.join(f,sf) for sf in subff]
            ff00.extend(subff)

        i = 0

        chs_all_dict = {}
        py_all_dict = {}

        for subff in ff00:
            wavfs = os.listdir(subff)
            wavfs = [wavf for wavf in wavfs if wavf.endswith(".wav")] # 过滤审查一遍
            for wavf in wavfs:
                print(f"\r{i},{wavf}.",end="\0",flush=True)
                i+=1

                line = file_label_map.get(wavf,None)
                pyline = self.pymap.sent2pylist(line)

                chs_dict = self.count_label(line)
                py_dict = self.count_label(pyline)
                chs_all_dict = self.merge_count_label(chs_dict, chs_all_dict)
                py_all_dict = self.merge_count_label(py_dict, py_all_dict)

                if line is not None: # 存在标签，可以生成
                    fpre,_ = os.path.splitext(wavf)
                    txtfpath = os.path.join(subff,f"{fpre}.txt")
                    with open(txtfpath,"w",encoding="utf-8") as w:
                        w.write(f"{line}\n")
                        w.write(f"{pyline}\n")
                else:
                    print(f"file {wavf} not exists, please check the dataset.")

        self._write_count_result(chs_all_dict,py_all_dict)
        print("Primewords finished.\n")

class News2016zh(Cleaner):
    '''还未写完'''
    def gene_pinyin(self):
        '''
        https://github.com/brightmart/nlp_chinese_corpus中的新闻语料json版(news2016zh)
        :param dir_path: 包含json文件的目录
        :return:
        '''

        train_json = os.path.join(self.path, "news2016zh_train.json")
        valid_json = os.path.join(self.path, "news2016zh_train.json")
        os.makedirs(os.path.join(self.path, "train"), exist_ok=True)
        os.makedirs(os.path.join(self.path, "valid"), exist_ok=True)

        with open(train_json,encoding="utf-8") as f:
            for i,line in enumerate(f):
                jstr = json.loads(line)
                content = jstr["content"]
                # self.pymap.sent2pylist()