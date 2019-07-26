# -*- coding: utf-8 -*-
# @Author: zhaoliang
# @Date:   2019-07-11 14:40:06
# @Email:  1318525510@qq.com
# @Last Modified by:   admin
# @Last Modified time: 2019-07-18 16:01:09
'''
基于规则构建BIESO数据
规则为 基于输入的字典进行最大正则匹配，认为一个词只属于一个类别，如果当他输入某个类别时，将这个词的BIES打上对应类别的标签
训练时 将字典随机删除一定比例，用一个不全的数据去训练模型
测试时 用全部字典生成序列
'''

import pandas as pd
import re
import random
import jieba
import os
class BIESO(object):
    """
    基于规则抽取文件中的BIESO数据，其中规则由用户字典输入，每一个字典为一个类别的内容
    """
    def __init__(self):
        self.random_cut_dict = False # 在训练时，采用随机删除删除字典的方式作为袋外词，默认为否
        self.random_cut_dict_probability = 0.3 #随机删除的字典的词的概率,原来是0.2
        self.dict_list = []
        self.dicts_name = []


    def add_dict(self,file_dict,dict_name):
        """
        构建字典
        :param file_dict: 字典数据文件名，其中每一行为一个实体
        :param name: 这个实体的名字，以便在BISEO中进行标注
        :return:
        """
        A = []
        with open(file_dict, 'r', encoding='utf-8') as f:
            for i in f.readlines():
                if i.strip() !='':
                    A.append(i.strip())
        A.sort(key=lambda x: len(x),reverse=True)
        if self.random_cut_dict == True:#在训练时随机删除一部分
            random_cut_dict_list =[]
            cut_list = []
            for i in range(int(len(A)*self.random_cut_dict_probability)):
                cut_list.append(random.randrange(0,len(A)))
            B = A[:]
            f=open('训练时删除的{}字典数据.txt'.format(dict_name),'w',encoding='utf-8')
            for i in cut_list:
                f.write(A[i])
                f.write('\n')
                try:
                    B.remove(A[i])
                except:
                    # print('改词重复出现',A[i])
                    pass
            f.close()
            A = B
        self.dict_list.append([A,dict_name])
        self.dicts_name.extend(A)


    def get_bieso_byFFM(self,f_data,f_write_name,max_len,column_name):
        '''
        构建BIO数据，第一列为字，第二例为BIESO标签
        :param f_data: 输入的dataframe数据，每一行为一个药品说明书，其中column_name列是我们要抽取的数据
        :param f_write_name: 将抽取得到的结果要写入的文件名
        :param max_len: 最大正则匹配的最大长度，应该为在文件中出现的实体名的最长长度
        :return:
        '''
        for data_i in range(0, f_data.shape[0]):
            print('抽取第{}行数据'.format(data_i))
            entity_num = 0
            with open(f_write_name+('训练' if self.random_cut_dict else '测试')+'.txt', 'a', encoding='utf-8') as f:
                str_shuomingshu = f_data[column_name].loc[data_i]
                str_shuomingshu = re.sub(pattern='\t|\s|\n', repl='', string=str_shuomingshu)
                while str_shuomingshu != '':
                    flag = 0
                    for dict_i in self.dict_list:
                        word = str_shuomingshu[:max_len]
                        while 1:
                                if word in dict_i[0]:
                                    # print([word, dict_i[1]])
                                    if len(word) == 1:
                                        f.write('\t'.join([word, 'S-{}'.format(dict_i[1]), '\n']))
                                    elif len(word) == 2:
                                        f.write('\t'.join([word[0], 'B-{}'.format(dict_i[1]), '\n']))
                                        f.write('\t'.join([word[1], 'E-{}'.format(dict_i[1]), '\n']))
                                    elif len(word) > 2:
                                        f.write('\t'.join([word[0], 'B-{}'.format(dict_i[1]), '\n']))
                                        for word_compontet in range(1, len(word) - 1):
                                            f.write('\t'.join([word[word_compontet], 'I-{}'.format(dict_i[1]), '\n']))
                                        f.write('\t'.join([word[-1], 'E-{}'.format(dict_i[1]), '\n']))
                                    flag = 1
                                    entity_num += flag
                                    break
                                else:
                                    if len(word) == 1:
                                        break
                                    else:
                                        word = word[:len(word) - 1]

                        if flag == 1:
                                break
                        else:
                                continue

                    if flag == 0:
                        f.write('\t'.join([word, 'O', '\n']))

                    str_shuomingshu = str_shuomingshu[len(word):]
                # f.write('\t'.join(['END', 'END', '\n'])) #每个药品说明书用END隔开
            if entity_num < 5:
                print('第{}行药品说明书抽取失败，未识别出实体或抽取数量过少，需要进一步人工处理'.format(data_i))


    def get_bieso_by_jieba(self,f_data,f_write_name,column_name):
        '''
        利用结巴分词，先分词，在进行标注
        :param f_data:
        :param f_write_name:
        :param column_name:
        :return:
        '''
        f=open(f_write_name+('训练' if self.random_cut_dict else '测试')+'.txt', 'w', encoding='utf-8')
        for data_i in range(0, f_data.shape[0]):
            print('抽取第{}行数据'.format(data_i))
            entity_num = 0
            # with open(f_write_name+('训练' if self.random_cut_dict else '测试')+'.txt', 'a', encoding='utf-8') as f:
            str_shuomingshu = f_data[column_name].loc[data_i]
            str_shuomingshu = re.sub(pattern='\t|\s|\n', repl='', string=str_shuomingshu)
            seg_list = jieba.cut(str_shuomingshu)
            for word in seg_list:
                if word not in  self.dicts_name:
                    for character in word:
                        f.write('\t'.join([character, 'O', '\n']))
                else:
                    for dict_i in self.dict_list:
                        if word in dict_i[0]:
                            # print([word, dict_i[1]])
                            if len(word) == 1:
                                f.write('\t'.join([word, 'S-{}'.format(dict_i[1]), '\n']))
                            elif len(word) == 2:
                                f.write('\t'.join([word[0], 'B-{}'.format(dict_i[1]), '\n']))
                                f.write('\t'.join([word[1], 'E-{}'.format(dict_i[1]), '\n']))
                            elif len(word) > 2:
                                f.write('\t'.join([word[0], 'B-{}'.format(dict_i[1]), '\n']))
                                for word_compontet in range(1, len(word) - 1):
                                    f.write('\t'.join([word[word_compontet], 'I-{}'.format(dict_i[1]), '\n']))
                                f.write('\t'.join([word[-1], 'E-{}'.format(dict_i[1]), '\n']))
                    entity_num+=1

            f.write('\t'.join(['END', 'END', '\n'])) #每个药品说明书用END隔开
            if entity_num < 5:
                print('第{}行药品说明书抽取失败，未识别出实体或抽取数量过少，需要进一步人工处理'.format(data_i))
        f.close()
    



def run():
    f_data = pd.read_csv('../寻医问药网站数据/寻医问药药物数据_enconding_gb18030.csv',encoding='GB18030')
    print(f_data.shape)
    jieba.load_userdict('../标准词典/药物所有成份.txt',)
    jieba.load_userdict('../标准词典/疾病与症状_不区分.txt')
    jieba.load_userdict('../标准词典/病人属性.txt')

    bieso = BIESO()
    bieso.random_cut_dict = True #生成部分词典匹配的训练语聊，在添加字典时会随机删除一部分规则
    bieso.add_dict('../标准词典/药物所有成份.txt','component')
    bieso.add_dict('../标准词典/疾病与症状_不区分.txt','disease&symptom')
    bieso.add_dict('../标准词典/病人属性.txt','people')
    bieso.get_bieso_by_jieba(f_data=f_data,f_write_name='BIESO',column_name='药品说明书')

    bieso = BIESO()
    bieso.random_cut_dict = False #生成部分词典匹配的测试语聊
    bieso.add_dict('../标准词典/药物所有成份.txt','component')
    bieso.add_dict('../标准词典/疾病与症状_不区分.txt','disease&symptom')
    bieso.add_dict('../标准词典/病人属性.txt','people')
    bieso.get_bieso_by_jieba(f_data=f_data,f_write_name='BIESO',column_name='药品说明书')

    '''
    # 采用正向最大匹配的方法得到在数据中的所有词，得到分词结果
    # 该方法可以得到症状、成份的最大匹配结果（葡萄糖和葡萄），但是因为每次都要对整个字典进行查找速度很慢
    # 该方法的加速方法是将字典根据字符长度得到不同长度的小字典，在每个窗口内只查找对应长度的字典
    bieso.get_bieso(f_data=f_data,f_write_name='BIO',max_len=20,column_name='药品说明书')

    '''


if __name__ =='__main__':
    run()



