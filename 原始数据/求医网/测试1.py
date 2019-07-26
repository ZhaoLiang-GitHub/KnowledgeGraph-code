# -*- coding: utf-8 -*-
# @Author: zhaoliang
# @Date:   2019-07-18 14:40:06
# @Email:  1318525510@qq.com
# @Last Modified by:   admin
# @Last Modified time: 2019-07-18 14:51:38
import re
import pandas as pd

 
class Disease_Symptom():
    '''
    该类用来处理从求医网获得的数据，根据该数据构造 疾病-症状 的层级结构
    '''

    def __init__(self, dataframe):
        self.all_disease = []
        self.all_symptom = []
        self.dataframe = dataframe
        self.id_symptom = []
        self.id_disease = []

    def get_id_disease(self):
        '''
        在输入的dataframe中的"疾病链接"这一字段中中抽取疾病，并且在"结构"中抽取出对应疾病的别名并保存在同义词文件中
        :return: 同义词文件中用中文逗号隔开，第一个词是标准疾病
        '''
        f = open('./生成文件/疾病同义词字典.txt', 'a', encoding='utf-8')
        f.seek(0)
        f.truncate()
        num_disease = 0
        num_alias = 0
        for i in range(self.dataframe.shape[0]):
            id = self.dataframe['疾病链接'].loc[i]
            disease = self.dataframe['结构'].loc[i].strip().split('-->')[-1]
            disease_name_str = self.dataframe['别名'].loc[i].replace('\'', '').replace('[', '').replace(']', '')
            disease_name_str = re.sub(pattern='.*暂无', string=disease_name_str, repl='')
            disease_name_str = re.sub(pattern='\s', string=disease_name_str, repl='')
            if disease_name_str != '':
                disease_name_list = re.split(pattern='、|,|，|\s', string=disease_name_str)
                disease_name_list.append(disease.strip().replace('.', ''))
                num_disease += 1
                num_alias += len(disease_name_list)
                f.write(disease + '，' + '，'.join(disease_name_list) + '\n')
            self.id_disease.append([id, disease])
        print('在求医网中共有{}个疾病存在同义词，共有{}个疾病同义词'.format(num_disease, num_alias))

    def get_id_symptom(self, wrong_wrod_list_add):
        '''
        在dataframe中的"相关症状"字段中基于规则匹配对应的症状
        :param wrong_wrod_list_add: 分割错误的词，如果得到的症状在分割错误词list中则不做处理
        :return: 将分割得到的长度小于1大于10的词也添加入了错误词list并保存在之前的TXT文件中，以便以后人工处理
        '''
        wrong_wrod_flie = open(wrong_wrod_list_add, 'a', encoding='utf-8')
        for i in range(self.dataframe.shape[0]):
            SYMPTOM_LIST = []
            id = self.dataframe['疾病链接'].loc[i]
            symptom_str_adjective = self.dataframe['相关症状'].loc[i]
            '''
            self.dataframe['相关症状'].loc[i]的实例：[['头痛', '干咳', '发烧', '详情>>'], ['一、', '病毒性肺炎常见症状', '\u3000\u3000两肺毛玻璃样粟粒样或结节样改变、干咳、乏力、肺纹理增粗、肺门增宽、高热', '\u3000', '\u3000二、病毒性肺炎症状', '\u3000\u3000本病临床表现一般较轻，*****
            该句子中有两个list组成，但是在写入CSV中是直接 str(list) 的操作，因此会带上方括号和引号等，需要通过正则去掉
            通常这句话有两个list，第一个list是规整的症状list；第二个list是对该疾病的进一步解释，在第二个list的第一句话"一、**疾病的常见症状,症状1、症状2、症状3,"通过规则将这句话中的症状拿出来
            '''
            symptom_str = symptom_str_adjective[1:-1]
            try:
                symptom_str_1 = symptom_str.split('], [')[0].replace('[', '').replace(']', '').replace('\'', '')
                symptom_str_1 = re.sub(pattern='详.*>?', string=symptom_str_1, repl='')
                symptom_str_1 = re.sub(pattern='\s', string=symptom_str_1, repl='')
                symptom_list_1 = symptom_str_1.split(',')
                # print(symptom_list_1,'\n')
                SYMPTOM_LIST.extend(symptom_list_1)  # 含有特殊字符：空字符串、None

                symptom_str_2 = symptom_str.split('], [')[1].replace('[', '').replace(']', '').replace('\'', '')
                symptom_str_2 = re.sub(pattern='\\\\[a-z]?[0-9]*', string=symptom_str_2, repl='')
                symptom_str_2 = re.sub(pattern='\s', string=symptom_str_2, repl='')
                symptom_str_2_match_list = re.findall(pattern='一?，?,?、.*?[常见症状|典型症状|临,?床表现]：?:?,.*?,', string=symptom_str_2)
                if len(symptom_str_2_match_list) == 0:
                    # print(id,'格式不一致，没有常见症状这样的表述')
                    # print(symptom_str_adjective,'\n')
                    pass
                else:
                    symptom_str_2_match = re.sub(pattern='一、.*?[常见症状|典型症状],', string=symptom_str_2_match_list[0], repl='')
                    symptom_str_2_match = re.sub(pattern='，|,|，|。|等.*|或|即|和|及', string=symptom_str_2_match, repl='、')
                    symptom_str_2_match = re.sub(pattern='[0-9]\.', string=symptom_str_2_match, repl='、')
                    symptom_str_2_match = re.sub(pattern='[①②③④⑤⑥⑦⑧⑨]', string=symptom_str_2_match, repl='')
                    symptom_str_2_match = re.sub(pattern=';|：', string=symptom_str_2_match, repl='')
                    symptom_str_2_match = re.sub(pattern='[（|\(][一二三四五六七八九十1234567890][）|\)]', string=symptom_str_2_match, repl='')
                    symptom_str_2_match = re.sub(pattern='轻度|轻微|局部|全身|上午|下午|晚上|傍晚|常见|偶见|罕见', string=symptom_str_2_match, repl='')
                    symptom_str_2_match = re.sub(pattern='.*有|以致|感觉|出现|时|有|如|当|的症状|俗称就是', string=symptom_str_2_match, repl='')


                    symptom_str_2_match = symptom_str_2_match.replace('（','(').replace('）','')

                    symptom_list_2 = re.split(pattern='、', string=symptom_str_2_match)
                    for symptom_list_2_i in symptom_list_2:
                        if '(' in symptom_list_2_i and ')' not in symptom_list_2_i:
                            wrong_wrod_flie.write(symptom_list_2_i + '\n')
                        elif ')' in symptom_list_2_i and '(' not in symptom_list_2_i:
                            wrong_wrod_flie.write(symptom_list_2_i + '\n')
                        else:
                            if len(symptom_list_2_i) > 1 and len(symptom_list_2_i) <= 10:
                                SYMPTOM_LIST.append(symptom_list_2_i)
                            else:
                                wrong_wrod_flie.write(symptom_list_2_i + '\n')
            except:
                # print('只有一个list',id)
                # print(symptom_str_adjective)
                symptom_str = re.sub(pattern='详.*>?', string=symptom_str, repl='').replace('[', '').replace(']','').replace('\'', '')
                symptom_str = re.sub(pattern='\s', string=symptom_str, repl='')
                symptom_list_1 = symptom_str.split(',')
                SYMPTOM_LIST.extend(symptom_list_1)

            finally:
                for SYMPTOM_LIST_i in SYMPTOM_LIST:
                    SYMPTOM_LIST_i = SYMPTOM_LIST_i.strip().replace('.', '')
                    self.id_symptom.append([id, SYMPTOM_LIST_i])

        wrong_wrod_flie.close()
        wrong_wrod_flie = open(wrong_wrod_list_add, 'r+', encoding='utf-8')
        wrong_wrod_flie_list = wrong_wrod_flie.readlines()
        wrong_wrod_flie_list = [wrong_wrod_flie_list_i for wrong_wrod_flie_list_i in wrong_wrod_flie_list if
                                wrong_wrod_flie_list_i.strip() != '']
        wrong_wrod_flie_list = list(set(wrong_wrod_flie_list))
        wrong_wrod_flie.seek(0)
        wrong_wrod_flie.truncate()
        wrong_wrod_flie_list.sort(key=lambda x: len(x))
        wrong_wrod_flie.write(''.join(wrong_wrod_flie_list))
        wrong_wrod_flie.close()

    def match_disease_symptom(self, wrong_wrod_list_add):
        '''
        将得到的"id-疾病"和"ID-症状"当ID相同时，构建症状-导致-疾病三元组，当症状或疾病出现在错误词中则不添加三元组
        :param wrong_wrod_list_add:
        :return:
        '''
        with open(wrong_wrod_list_add, 'r', encoding='utf-8') as f:
            wrong_wrod_list = f.readlines()
            wrong_wrod_list = [i.strip() for i in wrong_wrod_list]

        self.get_id_symptom(wrong_wrod_list_add)
        self.get_id_disease()
        f = open('./生成文件/求医网中症状导致疾病层级结构.txt', 'a', encoding='utf-8')
        f.seek(0)
        f.truncate()
        num = {'症状': 0, '导致': 0, '疾病': 0}
        entity = []
        for i in self.id_disease:
            for j in self.id_symptom:
                if i[0] == j[0]:
                    if i[1] != '' and i[1] != None and j[1] != '' and j[1] != None:
                        if i[1] not in wrong_wrod_list and j[1] not in wrong_wrod_list:
                            f.write(j[1] + '-导致-' + i[1] + '\n')
                            self.all_disease.append(i[1])
                            self.all_symptom.append(j[1])
                        if i[1] not in entity:
                            num['疾病'] += 1
                            entity.append(i[1])
                        if j[1] not in entity:
                            num['症状'] += 1
                            entity.append(j[1])
                        num['导致'] += 1

        print('在求医网中的症状->导致->疾病的层级结构数据如下所示\n\n实体或关系|数量\n:-:|:-:')
        for k, v in num.items():
            print(k, '|', v)

    def cover_rate(self, f_disease_add, f_symptom_add, flag=False):
        '''
        计算在求医网中的疾病症状和已有的疾病症状字典的覆盖率
        :param f_disease_add: 现有的疾病字典地址
        :param f_symptom_add: 现有的症状字典地址
        :param flag: 用来控制是否直接将新词写入在原有字典中，默认为否
        :return:
        '''
        f_symptom = open(f_symptom_add, 'r', encoding='utf-8')
        f_disease = open(f_disease_add, 'r', encoding='utf-8')
        f_disease = [i.strip() for i in f_disease]
        f_symptom = [i.strip() for i in f_symptom]

        same_disease = set(self.all_disease) & set(f_disease)
        same_symptom = set(self.all_symptom) & set(f_symptom)

        different_disease = list(set(self.all_disease) - set(same_disease))
        different_symptom = list(set(self.all_symptom) - set(same_symptom))
        print('\n现有疾病字典对求医网的疾病的覆盖率为{}%'.format(str((len(same_disease) / len(set(self.all_disease))) * 100)[:5]))
        print('现有疾病字典对求医网的症状的覆盖率为{}%'.format(str((len(same_symptom) / len(set(self.all_symptom))) * 100)[:5]))
        print('在求医网中新增的疾病实体{}个'.format(len(same_disease)))
        print('在求医网中新增的症状实体{}个'.format(len(same_symptom)))
        

        if flag == False:
            with open('生成文件/求医网中新出现的疾病.txt', 'w', encoding='utf-8') as f:
                different_symptom.sort(key=lambda x: len(x))
                f.write('\n'.join(different_disease))
            with open('生成文件/求医网中新出现的症状.txt', 'w', encoding='utf-8') as f:
                different_symptom.sort(key=lambda x: len(x))
                f.write('\n'.join(different_symptom))
        elif flag == True:
            with open(f_disease_add, 'a', encoding='utf-8') as f:
                f.write('\n'.join(different_disease))
            with open(f_symptom_add, 'a', encoding='utf-8') as f:
                f.write('\n'.join(different_symptom))


if __name__ == '__main__':
    dataframe = pd.read_csv('dis(3).csv')
    wrong_wrod_list_add = './生成文件/错误分割的词.txt'
    f_disease_add = '../标准词典/疾病.txt'
    f_symptom_add = '../标准词典/症状.txt'
    flag = False  # 在求医网中的新出现的词，是否要直接保存在疾病和症状的字典里,默认为不直接保存而是写在一个新文件中，以便后期人工处理

    disease_symptom = Disease_Symptom(dataframe)
    disease_symptom.match_disease_symptom(wrong_wrod_list_add)
    disease_symptom.cover_rate(f_disease_add, f_symptom_add, flag)
