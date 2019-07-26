# -*- coding: utf-8 -*-
# @Author: zhaoliang
# @Date:   2019-06-11 14:40:06
# @Email:  zhaoliang1@interns.chuangxin.com
# @Last Modified by:   admin
# @Last Modified time: 2019-07-22 15:13:05
'''
将寻医问药数据中的实体抽取出来并保存在CSV文件中，之后一并导入，
'''
import re
import pandas as pd
import jieba


def set_global_var():
    global JINJI
    global SHUXING
    global FENLEI
    global CHENGFEN
    global GONGNENGZHUZHI

    JINJI = ['老年用药','孕妇及哺乳期妇女用药','警告/警示语','注意事项','禁忌', '儿童用药','药物相互作用','不良反应']

    # 药物属性值，用字符串保存
    SHUXING = ['药品有效期','分子量','性状','执行标准','说明书修订日期','药理作用','剂型','贮藏','用法用量','药物过量','药代动力学']

    # 药物分类，例如 "本品为矿物质类非处方药药品"
    FENLEI = ['作用类别']

    # 药物成分，可能会有禁忌关系
    CHENGFEN = ['成份', '分子式','化学名称']

    #功能主治
    GONGNENGZHUZHI = ['功能主治']

class EntityRelationship(object):
    '''
    抽取文件的实体以便进行关系构建
    '''
    def __init__(self,dataframe):
        '''

        :param dataframe: 需要被抽取关系的dataframe对象
        dict_list 用书输入字典列表，每一个元素为[[dict_i,name]] dict_i为某一个具体字典内容，name 为该字典的名字
        dataframe 为抽取的dataframe文件
        all_dataframe_entity 为dataframe文件中抽取出来的实体，每一行为一个向量
        '''
        self.dict_list = [] #所有的输入字典，每一个元素[实体,实体类别]
        self.dataframe = dataframe # 输入的dataframe对象
        self.data_all_entity = [] # 抽取出来的实体，每一行是一个字典
        self.all_medicine_name = [] #在数据中出现过的所有药物名字，在原始数据中的"药物名字"列有厂家名，在这里去掉了
        self.taboo_relation_list = []
        self.relationship_tuple_list=[]
        self.relationship_dict = {}
        self.dict_name_list = []


    def add_dict(self,file_dict,dict_name):
        """
        构建字典
        :param file_dict: 字典数据文件名，其中每一行为一个实体
        :param name: 这类实体的名字，在以后用于关系抽取
        :return:
        """
        A = []
        with open(file_dict, 'r', encoding='utf-8') as f:
            for i in f.readlines():
                if i.strip() !='':
                    A.append([i.strip(),dict_name])
        A.sort(key=lambda x: len(x),reverse=True)
        self.dict_name_list.append(dict_name)
        self.dict_list.extend(A)


    def write_dict(self):
        dict_dataframe = pd.DataFrame(self.dict_list,columns=['名称','标签'])
        dict_dataframe  = dict_dataframe.drop_duplicates()
        dict_dataframe.to_csv('../生成文件/导入的字典数据中的实体.csv',index=False,encoding='utf-8')#字典中的实体，先保存起来，一并导入
        print('导入的字典数据中实体数目{},具体的数目：'.format(dict_dataframe.shape[0]))
        print(dict_dataframe['标签'].value_counts())
        print('\n')


    def get_entity_from_string_by_rule(self,string):
        '''
        从句子中基于规则抽取在这个句子中出现的实体，规则为在这个句子中是否出现了字典中的词
        :param string:
        :param dict_list: 输入的字典list,其中每个列表元素为[[dict_i_list],dict_name]第一个元素为某个字典实体的list第二个实体为该字典的名字，名字用于以后分类
        :return:
        '''
        result = []
        for dict_entity in self.dict_list:
                if dict_entity[0] in string:
                    # print(dict_entity)
                    # print([dict_entity, dict_i[1]])
                    result.append(dict_entity[0])
        return result


    def get_entity_from_string_by_FMM(self,string,max_len,label_list):
        '''
        完全是基于人工写的最大正向，可以采用先分词在最大匹配
        因为在成份（中药材，化学药）、疾病（疾病、症状、证型）数据中存在重叠关系（葡萄-葡萄糖、头痛-偏头痛）
        如果单纯的采用字符串匹配的方法，会同时匹配出两个结果，在这里采用最大正向匹配的方法
        :param string: 需要匹配的字符串
        :param max_len: 在最大正则匹配的最大窗口
        :param string_label: 对应的需要去查找的字典的标签，只要在这个标签内的字典中去查找,输入的是一个list，每个元素是一个字典标签
        :return:
        '''
        dict_label_list = [i for i in self.dict_list if i[1] in label_list] # 找到所需要的对应的字典数据
        dict_label_list.sort(key=lambda x:len(x))
        result = []

        while string != '':
            word = string[:max_len]
            while 1:
                if word in dict_label_list:
                    result.append(word)
                    break
                else:
                    if len(word) == 1:
                        break
                    else:
                        word = word[:len(word) - 1]
            string = string[len(word):]
        return result


    def get_entity_from_string_by_jieba(self,string):
        '''
        利用结巴分词，先分词，在查找是不是在字典当中
        :param f_data:
        :param f_write_name:
        :param column_name:
        :return:
        '''
        result = []
        seg_list = jieba.cut(string)
        for word in seg_list:
            for dict_entity in self.dict_list:
                if dict_entity[0] == word :
                    result.append(dict_entity[0])
        return result


    def get_entity_from_dataframe(self):
        '''
        得到寻医问药数据中的每一行的实体，其中一部分是字符串，只有成份、功能主治、相关疾病是分开的
        :return:
        '''
        self.data_all_entity = []
        entity_dataframe = []
        for i in range(self.dataframe.shape[0]):
        # for i in range(10):
            line = '    '+self.dataframe['药品说明书'].loc[i]
            line_entity_dict = {'老年用药': '', '孕妇及哺乳期妇女用药': '', '警告/警示语': '', '注意事项': '', '禁忌': '', '儿童用药': '',
                                '药物相互作用': '', '不良反应': '',
                                '药品有效期': '', '分子量': '', '性状': '', '执行标准': '', '说明书修订日期': '', '药理作用': '', '剂型': '',
                                '贮藏': '', '用法用量': '', '药物过量': '', '药代动力学': '',
                                '作用类别': '', '成份': '', '分子式': '', '化学名称': '', '功能主治': '',  '药品网页链接': '',
                                '药品名': '', '生产企业': '', '疾病': '', '药品详细分类': '','通用名称':''}
            line_entity_dict['药品网页链接'] = self.dataframe['药品网页链接'].loc[i]
            line_entity_dict['药品名'] = self.dataframe['药品名'].loc[i]
            line_entity_dict['生产企业'] = self.dataframe['生产企业'].loc[i]
            line_entity_dict['疾病'] = self.dataframe['相关疾病'].loc[i]
            line_entity_dict['药品详细分类'] = self.dataframe['药品详细分类'].loc[i]


            namedic = {}
            p1 = re.compile(r' {4,}([^\d（●-【()]\S{1,20}?):')
            namelist = p1.findall(line)
            for i in namelist:
                namedic[i] = namedic.get(i, 1) + 1
            namesort = sorted(namedic.items(), key=lambda x: x[1], reverse=True)
            # print(namesort)
            names = [i[0] for i in namesort]
            p = re.compile(r'-|感染|革兰|疾病|：|罕有|罕见|\d|者|⑴|⑶|⑹|⒊|（|\(|\S+[病炎剂菌]')
            for i in range(len(names) - 1, -1, -1):  # print(names[i])
                if p.search(names[i]):
                    names.pop(i)
            for i in ['桔子味', '香草味', '准确的', '消化道贾第虫病', '口服时发现以下不良反应', '此时，可以采取以下措施', '如下', '⑴', '⑶', '⑹',
                      '儿童一日两次，每次按下列剂量口服', '例如', '胃内pH值', '强迫性神经症', '持续性高血压', '收缩压和舒张压升高', '瞳孔扩大',
                      '从本品转换为维生素K拮抗剂治疗', '胃内pH值', 'NMS的控制包括', '强迫性神经症', '惊恐障碍', '社交恐怖症/社交焦虑症',
                      '肾/肝功损害', 'ESRD', '麻醉', '心血管系统', '或遵医嘱。剂型', '血液和淋巴系统紊乱', '神经系统紊乱',
                      '外伤、中毒和手术并发症', '泌尿生殖系统', '酒精', '西咪替丁', '地西泮', '食欲减退。用法用量', '躁狂发作',
                      '预防双相情感障碍复发', '静脉注射', '静脉输注', '置于儿童接触不到处!成份', '钙拮抗剂', '性蛋白酶。药物过量',
                      '致癌和致突变现象动物实验未观察到。药物过量', '详见背面使用讲解。剂型', '药物蓄积。药理作用', '锥体束外反应',
                      '心血管作用', '血液学', '皮肤', '抗胆碱能', '胃肠道', '精神抑制药可提高泌乳素浓度', '分支杆菌',
                      '当皮损消退后，酌情维持治疗。不良反应', '②镇痛', '口服抗凝剂', '溶栓剂和抗血小板药物',
                      'ACE抑制剂和血管紧张素II受体拮抗剂', '环孢菌素', '宫内避孕装置', '氨甲喋呤', '消胆胺']:
                if i in names:
                    names.remove(i)
            # print(names)

            slist = line.split('    ')[1:]
            slen = []
            dic = {i: '尚不明确' for i in names} #该药品说明书中按照标签拿出来的数据
            loc = []
            for i in range(len(slist)):
                flag = 0
                slen.append(len(slist[i]) + 4 + flag)
                item = slist[i].split(':')[0]
                if item.startswith(' '):
                    item = item[1:]
                    flag = 1
                if item and item in names:
                    loc.append((i, item, flag))
            for i in range(len(loc)):
                l = loc[i][0]
                item = loc[i][1]
                flag = loc[i][2]
                if i == 0 or i == len(loc) - 1:
                    dic[item] = slist[l][len(item) + 1 + flag:]
                else:
                    dic[item] = ''.join(slist[l:loc[i + 1][0]])[len(item) + flag + 1:]
            # print(dic)

            xianguanjibing_list = []
            for xiangguanjibing_str_i in line_entity_dict['疾病'].strip().split('、'):
                xianguanjibing_list.append(xiangguanjibing_str_i)
            line_entity_dict['疾病'] = xianguanjibing_list
            yaopinxiangxifenlei_str = re.sub(pattern='\'|\[|\]：|疾病|:|：|]',string=line_entity_dict['药品详细分类'],repl='')
            yaopinxiangxifenlei_list = []
            for yaopinxiangxifenlei_str_i in yaopinxiangxifenlei_str.strip().split(','):
                yaopinxiangxifenlei_list.append(yaopinxiangxifenlei_str_i)
            line_entity_dict['药品详细分类'] = yaopinxiangxifenlei_list
            # print(line_entity_dict['药品详细分类'])


            for key in dic.keys():
                if key in CHENGFEN :
                    '''
                    # 基于字符串匹配 if 实体 in 字符串 ，这样会同时匹配出 葡萄 和葡萄糖两个实体，但是速度快
                    # line_entity_dict['成份'] = list(set(self.get_entity_from_string_by_rule(dic[key])))
                    # 基于正向最大正则匹配的，会找到在字典中的最长的字符串，但是速度很慢
                    # line_entity_dict['成份'] = list(set(self.get_entity_from_string_by_FMM(string=dic[key],max_len=10,label_list= ['中成药成份','西药成份'] )))
                    '''
                    # 基于结巴分词，然后在进行匹配
                    line_entity_dict['成份'] = list(set(self.get_entity_from_string_by_jieba(dic[key])))

                    
                elif key in GONGNENGZHUZHI:
                    '''
                    # 基于字符串匹配 if 实体 in 字符串 ，这样会同时匹配出 葡萄 和葡萄糖两个实体，但是速度快
                    line_entity_dict['疾病'].extend(self.get_entity_from_string_by_rule(dic[key]))
                    # 基于正向最大正则匹配的，会找到在字典中的最长的字符串，但是速度很慢
                    line_entity_dict['疾病'].extend(
                        list(set(self.get_entity_from_string_by_FMM(string=dic[key], max_len=10,label_list=['疾病', '症状', '中医证型']))))
                    '''
                    # 基于结巴分词，然后在进行匹配
                    line_entity_dict['成份'] = list(set(self.get_entity_from_string_by_jieba(dic[key])))

                else:
                    line_entity_dict[key] = dic[key]

            for line_entity_dict_key in line_entity_dict.keys():
                if line_entity_dict[line_entity_dict_key] == '' or line_entity_dict[line_entity_dict_key] == None:
                    pass
                else:
                    if type(line_entity_dict[line_entity_dict_key]) == str:
                        entity_dataframe.append([line_entity_dict[line_entity_dict_key], line_entity_dict_key])
                    else:
                        for i in line_entity_dict[line_entity_dict_key]:
                            entity_dataframe.append([i, line_entity_dict_key])
            yaopinmin = line_entity_dict['药品名'].split(' ')[-1]  # 去掉了厂商
            if yaopinmin!='':
                self.all_medicine_name.append([yaopinmin,line_entity_dict['药品网页链接']])
            self.data_all_entity.append(line_entity_dict)


        entity_dataframe = pd.DataFrame(entity_dataframe, columns=['实体', '类型'])
        print('去重前的寻医问药实体个数{}'.format(entity_dataframe.shape[0]))
        entity_dataframe = entity_dataframe.drop_duplicates(['实体'])
        print('去重后的寻医问药实体个数{}，并将该实体保存在文件中,具体实体个数是'.format(entity_dataframe.shape[0]))
        print(entity_dataframe['类型'].value_counts())
        entity_dataframe_kg = entity_dataframe.loc[entity_dataframe['类型'].isin(['药品网页链接','成份','疾病'])]
        entity_dataframe_shuxing = entity_dataframe.drop(labels=entity_dataframe_kg.axes[0])
        entity_dataframe_kg.to_csv('../生成文件/寻医问药数据中抽取的实体.csv', index=False,encoding='utf-8')
        entity_dataframe_shuxing.to_csv('../生成文件/寻医问药数据中抽取的实体-属性实体不在图谱中展示.csv', index=False,encoding='utf-8')


    def get_write_tabbo(self):
        # tabbo_label = ['忌服','禁用','酌减', '敏感', '慎用', '小心谨慎', '不适用', '减量', '慎重给药', '减少剂量', '延长给药间期', '肾功能减退', '不良反应', '酌情减少', '谨慎用药',
        #          '不可服用', '适当减少', '减量应用']
        tabbo_label = ['忌服','禁用',  '慎用', '不适用', '不可服用']
        relation_num = {'药物-禁忌-病人':0,'药物-禁忌-药物':0,'药物-禁忌-疾病或症状':0,'药物-禁忌-成份':0}
        dingdang_demo =[]
        for line in self.data_all_entity :
            for tabbo in tabbo_label:
                if tabbo in line['孕妇及哺乳期妇女用药']:
                    self.taboo_relation_list.append([line['药品网页链接'],'禁忌','孕妇及哺乳期妇女','病人属性'])
            
                    yaopinmin = line['药品名'].split(' ')[-1]  # 去掉了厂商
                    dingdang_demo.append([yaopinmin,'禁忌','孕妇及哺乳期妇女','病人属性'])
                    dingdang_demo.append([line['通用名称'],'禁忌','孕妇及哺乳期妇女','病人属性'])
            
                    relation_num['药物-禁忌-病人'] +=1
                if tabbo in line['老年用药']:
                    self.taboo_relation_list.append([line['药品网页链接'], '禁忌', '老年人','病人属性'])
            
                    yaopinmin = line['药品名'].split(' ')[-1]  # 去掉了厂商
                    dingdang_demo.append([yaopinmin,'禁忌','老年人','病人属性'])
                    dingdang_demo.append([line['通用名称'],'禁忌','老年人','病人属性'])
            
                    relation_num['药物-禁忌-病人'] +=1
                if tabbo in line['儿童用药']:
                    self.taboo_relation_list.append([line['药品网页链接'],'禁忌','儿童','病人属性'])
            
                    yaopinmin = line['药品名'].split(' ')[-1]  # 去掉了厂商
                    dingdang_demo.append([yaopinmin,'禁忌','儿童','病人属性'])
                    dingdang_demo.append([line['通用名称'],'禁忌','儿童','病人属性'])
            
                    relation_num['药物-禁忌-病人'] +=1
                '''
                tabbo_people= {'儿童':'儿童', '小儿':'儿童', '婴幼儿':'儿童', '青少年':'儿童', '婴儿':'儿童', '新生儿':'儿童', '早产儿':'儿童',
                               '年老体弱者':'老年人', '老年人':'老年人',
                               '孕妇及哺乳期妇女':'孕妇及哺乳期妇女','妊娠期':'孕妇及哺乳期妇女', '怀孕期':'孕妇及哺乳期妇女', '经期':'孕妇及哺乳期妇女', '月经期':'孕妇及哺乳期妇女', '孕期':'孕妇及哺乳期妇女', '孕妇':'孕妇及哺乳期妇女', '哺乳期':'孕妇及哺乳期妇女', '哺乳妇女':'孕妇及哺乳期妇女', '生育年龄有生育要求者':'孕妇及哺乳期妇女',
                               '高空作业者':'特殊职业', '驾驶员':'特殊职业', '机械操作者':'特殊职业', '驾驶车辆':'特殊职业', '管理机器':'特殊职业', '高空作业':'特殊职业', '使用免疫抑制剂者':'特殊职业', '身体壮实不虚者':'特殊职业', '运动员':'特殊职业'}
                '''
            f_write_jinji = open('../生成文件/寻医问药数据中的禁忌字符串.txt','a',encoding='utf-8')
            f_write_jinji.seek(0)
            f_write_jinji.truncate(0)

            for entity in self.dict_list:
                    string_jinji = line['禁忌']
                    if string_jinji != '' and string_jinji != None and '尚不明确' not in string_jinji:	
                        f_write_jinji.write(string_jinji)
                        f_write_jinji.write('\n')
                        if entity[0] in string_jinji :
                            if entity[0] not in line['成份'] and entity[0] not in line['疾病']:
                                self.taboo_relation_list.append([line['药品网页链接'],'禁忌',entity[0],entity[1]])
		            
                                yaopinmin = line['药品名'].split(' ')[-1]  # 去掉了厂商
                                dingdang_demo.append([yaopinmin, '禁忌', entity[0],entity[1]])
                                dingdang_demo.append([line['通用名称'], '禁忌', entity[0],entity[1]])
                                if entity[1] == '病人属性':     relation_num['药物-禁忌-病人'] += 1
                                elif entity[1] == '疾病或症状': relation_num['药物-禁忌-疾病或症状'] += 1
                                else:                         relation_num['药物-禁忌-成份'] += 1
                            else:
                                # 当存在成份（西药化学式、中药材）出现在了该药品的禁忌数据中时，
                                # 经查看，该情况大部分都是对该药品的某种成份过敏导致的禁忌，在这里不作处理，因为每个药物对含有的成份如果存在过敏反应都是禁忌关系

                                # 当存在疾病（症状、疾病、证型）出现在了该药品的禁忌数据中时，
                                # 经常看，该情况存在1疾病分词错误，2"因为含有治疗心脏病的的成份，所以对患有感冒的病人禁用"
                                # 这两种情况都是错误的禁忌关系，在此不做处理
                                pass


            for medicine_name in self.all_medicine_name:
                # if medicine_name[0] in line['禁忌'] or medicine_name[0] in line['警告/警示语'] or medicine_name[0] in line['注意事项']:
                if medicine_name[0] in line['禁忌'] :
                    self.taboo_relation_list.append([line['药品网页链接'], '禁忌', medicine_name[1],'药品网页链接'])
                    yaopinmin = line['药品名'].split(' ')[-1]  # 去掉了厂商
                    dingdang_demo.append([yaopinmin,'禁忌', medicine_name[0],'药品网页链接'])
                    dingdang_demo.append([line['通用名称'],'禁忌', medicine_name[0],'药品网页链接'])
            
                    relation_num['药物-禁忌-药物']+=1

        relationship_dataframe = pd.DataFrame(self.taboo_relation_list, columns=['开始', '关系', '结束','节点类型'])
        relationship_dataframe = relationship_dataframe.drop_duplicates()
        print('在寻医问药数据中有{}个禁忌关系，具体数目：'.format(relationship_dataframe.shape[0]))
        for k,v in relation_num.items():
            print(k,'\t',v)
        print('\n')
        relationship_dataframe.to_csv('../生成文件/寻医问药数据中的禁忌关系.csv',index=False,encoding='utf-8')

        dingdang_demo_dataframe = pd.DataFrame(dingdang_demo,columns=['药品名','禁忌','禁忌节点','节点类型'])
        dingdang_demo_dataframe = dingdang_demo_dataframe.drop_duplicates()
        dingdang_demo_dataframe.to_csv('../生成文件/寻医问药数据中药品名的禁忌关系.csv',index=False,encoding='utf-8')


    def create_relationship(self, start='', relationgship='', end=''):
        if relationgship not in self.relationship_dict.keys():
            self.relationship_dict[relationgship] = 0
        for line in self.data_all_entity:
            if line[start] !=None and line[end] !=None and line[start] !='' and line[end] !='':
                if type(line[start]) ==list:
                    if type(line[end]) == list:
                        for start_i in line[start] :
                            for end_i in line[end]:
                                self.relationship_dict[relationgship] +=1
                                self.relationship_tuple_list.append([start_i,relationgship,end_i,start,end])
                    elif type(line[end]) == str:
                        for start_i in line[start] :
                            self.relationship_dict[relationgship] += 1
                            self.relationship_tuple_list.append([start_i,relationgship,line[end],start,end])
                elif type(line[start]) ==str:
                    if type(line[end] )== list:
                            for end_i in line[end]:
                                self.relationship_dict[relationgship] +=1
                                self.relationship_tuple_list.append([line[start],relationgship,end_i,start,end])
                    else:
                        self.relationship_dict[relationgship] += 1
                        self.relationship_tuple_list.append([line[start],relationgship,line[end],start,end])


    def write_relationship(self,flag):
        a = pd.DataFrame(self.relationship_tuple_list)
        zong = 0
        for i in self.relationship_dict.values():
            zong += i
        if flag==True:
            print('在寻医问药知识图谱中共有关系{}个具体数目如下:\n关系类型|数量\n:-:|:-:'.format(zong))
            for k, v in self.relationship_dict.items():
                print(k, '|', v)
            a.to_csv('../生成文件/寻医问药中抽取关系.csv',index=False,header=['开始','关系类型','结束','开始节点类型','结束节点类型'],encoding='utf-8')
            self.relationship_tuple_list =[]
            self.relationship_dict = {}
            print('\n')
            print('\n')
        else:
            print('在寻医问药知识图谱中共有属性关系{}个具体数目如下:\n关系类型|数量\n:-:|:-:'.format(zong))
            for k, v in self.relationship_dict.items():
                print(k, '|', v)
            a.to_csv('../生成文件/寻医问药中抽取关系-属性关系不在图谱中展示.csv',index=False,header=['开始','关系类型','结束','开始节点类型','结束节点类型'],encoding='utf-8')


def main():
    set_global_var()
    f_data = pd.read_csv('../data/xunyiwenyao/寻医问药药物数据_enconding_gb18030.csv',encoding='GB18030')
    zhongchengyaochengfen_add = '../data/dict/中成药成份.txt'
    xiyaochengfen_add = '../data/dict/西药成份.txt'
    bingrenshuxing_add ='../data/dict/病人属性.txt'
    jibing_add = '../data/dict/疾病.txt'
    zhengzhuang_add = '../data/dict/症状.txt'
    zhongyizhengxing_add = '../data/dict/中医证型.txt'
    suoyouzidian_add = '../data/dict/所有字典.txt'

    # 在jieba分词中添加我们的字典，所有字典时将之前的所有的字典添加进来的
    jieba.loda_userdict(suoyouzidian_add)

    get_dataframe_entity = EntityRelationship(f_data)
    # 成份的两个字典，在基于规则匹配的时候回出现重叠字符串匹配两次的情况，可以采用最大正向匹配的方法，在
    get_dataframe_entity.add_dict(zhongchengyaochengfen_add,'中成药成份')
    get_dataframe_entity.add_dict(xiyaochengfen_add,'西药成份')
    # 病人的一个属性字典
    get_dataframe_entity.add_dict(bingrenshuxing_add,'病人属性')
    # 疾病的三个字典
    get_dataframe_entity.add_dict(jibing_add,'疾病')
    get_dataframe_entity.add_dict(zhengzhuang_add,'症状')
    get_dataframe_entity.add_dict(zhongyizhengxing_add,'中医证型')
    get_dataframe_entity.write_dict()



    print('抽取寻医问药中的药物数据实体')
    get_dataframe_entity.get_entity_from_dataframe()#抽取药物说明书中的实体，一行是一列的抽取出来的实体结果,并将结果保存在CSV中
    print('实体抽取完成并保存在CSV文件中')

    print('构建禁忌关系')
    get_dataframe_entity.get_write_tabbo()#此时实体并未构建，禁忌关系可以只保存在CSV文件中，以后一并导入
    print('构建禁忌关系完成并保存在CSV文件中')

    print('抽取寻医问药数据中的关系')#此时关系并没有构建，而是保存在了csv文件中，以后一并导入\
    flag = True #需要在知识图谱中展示的关系时，flag设置为true，当不需要展示时设置为Flase
    get_dataframe_entity.create_relationship('药品网页链接','治疗','疾病')
    get_dataframe_entity.create_relationship('药品网页链接','成份是','成份')
    get_dataframe_entity.write_relationship(flag)
    
    flag = False
    get_dataframe_entity.create_relationship('药品网页链接','药品有效期是','药品有效期')
    get_dataframe_entity.create_relationship('药品网页链接','分子量是','分子量')
    get_dataframe_entity.create_relationship('药品网页链接','性状是','性状')
    get_dataframe_entity.create_relationship('药品网页链接','执行标准是','执行标准')
    get_dataframe_entity.create_relationship('药品网页链接','说明书修订日期是','说明书修订日期')
    get_dataframe_entity.create_relationship('药品网页链接','药理作用是','药理作用')
    get_dataframe_entity.create_relationship('药品网页链接','剂型是','剂型')
    get_dataframe_entity.create_relationship('药品网页链接','用法用量是','用法用量')
    get_dataframe_entity.create_relationship('药品网页链接','药代动力学是','药代动力学')
    get_dataframe_entity.create_relationship('药品网页链接','药品名是','药品名')
    get_dataframe_entity.create_relationship('药品网页链接','生产企业是','生产企业')
    get_dataframe_entity.create_relationship('药品网页链接','药品详细分类是','药品详细分类')
    get_dataframe_entity.create_relationship('药品网页链接','通用名称是','通用名称')
    get_dataframe_entity.write_relationship(flag)
    print('寻医问药中关系抽取完成并保存在CSV文件中')


if __name__ == '__main__':
    main()