# -*- coding: utf-8 -*-
# @Author: zhaoliang
# @Date:   2019-07-23 17:08:10
# @Email:  zhaoliang1@interns.chuangxin.com
# @Last Modified by:   admin
# @Last Modified time: 2019-07-25 18:25:02
import pandas as pd
import re
from py2neo import Graph, Node, Relationship, NodeMatcher




class HaoXinQingKG(object):
    def __init__(self):
        self.id_entity_relation_attribute = []  # 从好心情数据中抽取出来的关系， 药物ID-具体实体-两者关系-关系属性
        self.num_relation = {}
        self.num_entity = {'ID': 0}
        self.dict_list = []
        self.wrong_entity = [] # 在数据中新出现但是不知道怎么分类的实体，先将其保存下来，之后做分类
        self.new_entity = []  # 在数据中新出现的实体，每一个元素为 实体，实体类别


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
        self.dict_list.extend(A)


    def get_data(self):
        f = pd.read_excel('../data/haoxinqing/好心情_全部.xlsx')
        for i in range(f.shape[0]):
            id = f['num'].loc[i]  # 每个药品的唯一标识符，现在暂时用ID索引来表示
            chengfen = f['主要成分'].loc[i]  # 每个药品的处理之后的成份
            if type(chengfen) == float:
                chengfen =''
            chengfen_list = re.split(pattern='[，；、]',string=chengfen)
            for chengfen_list_i in chengfen_list:
                self.id_entity_relation_attribute.append([id,'包含',chengfen_list_i,'包含'])

            gongnengzhuzhi = f['标注的功能主治'].loc[i]  # 每个药物处理之后的功能主治
            if type(gongnengzhuzhi) == float:
                gongnengzhuzhi = ''
            gongnengzhuzhi_list = re.split(pattern='[，；、]',string=gongnengzhuzhi)
            for gongnengzhuzhi_list_i in gongnengzhuzhi_list:
                self.id_entity_relation_attribute.append([id,gongnengzhuzhi_list_i,'治疗','治疗'])



            buliangfanyin = f['不良反应_y'].loc[i]  # 每个药品处理之后的不良反应值，该值是一个str,切割之后是一个list，每个元素是 关系属性 :具体实体
            if type(buliangfanyin) == float:
                buliangfanyin = ''
            buliangfanyin = buliangfanyin.replace('\n', '').replace(':', '：')
            buliangfanyin_spit = buliangfanyin.split('；')
            try:
                buliangfanyin_list = [[ii.split('：')[0], ii.split('：')[1]] for ii in buliangfanyin_spit if ii != '']
            except:
                print('cuowu', buliangfanyin_spit)
                buliangfanyin_list = []
            for buliangfanyin_list_i in buliangfanyin_list:
                self.id_entity_relation_attribute.append([id, buliangfanyin_list_i[1], '不良反应', buliangfanyin_list_i[0]])

            zhuyishixiang = f['注意事项关系_x'].loc[i]  # 每个药物标注的注意事项，切割之后是一个list，每个元素是 关系属性：具体实体
            if type(zhuyishixiang) == float:
                zhuyishixiang = ''
            zhuyishixiang_split = zhuyishixiang.split('；')
            try:
                zhuyishixiang_list = [[ii.split('：')[0], ii.split('：')[1]] for ii in zhuyishixiang_split if ii != '']
            except:
                print('cuowu', zhuyishixiang)
                zhuyishixiang_list = []
            for zhuyishixiang_list_i in zhuyishixiang_list:
                self.id_entity_relation_attribute.append([id, zhuyishixiang_list_i[1], '注意事项', zhuyishixiang_list_i[0]])

            jinji = f['禁忌标注_x'].loc[i]  # 每个药物的禁忌，切割后每个元素是 关系属性:具体实体
            if type(jinji) == float:
                jinji = ''
            jinji_split = jinji.split('；')
            try:
                jinji_list = [[ii.split('：')[0], ii.split('：')[1]] for ii in jinji_split if ii != '']
            except:
                print('cuowu', jinji)
                jinji_list = []
            for jinji_list_i in jinji_list:
                self.id_entity_relation_attribute.append([id, jinji_list_i[1], '禁忌', jinji_list_i[0]])

            ertongyongyao = f['儿童标注'].loc[i]  # 每个药物对于儿童的使用情况，和之前的一样也是 关系属性：实体
            if type(ertongyongyao) == float:
                ertongyongyao = ''
            ertongyongyao_split = ertongyongyao.split('；')
            try:
                ertongyongyao_list = [[ii.split('：')[0], ii.split('：')[1]] for ii in ertongyongyao_split if ii != '']
            except:
                print('cuowu', ertongyongyao, i)
                ertongyongyao_list = []
            for ertongyongyao_list_i in ertongyongyao_list:
                self.id_entity_relation_attribute.append([id, ertongyongyao_list_i[1], '儿童用药', ertongyongyao_list_i[0]])


            laonianyongyao = f['老年标注'].loc[i]  # 每个药物对于老年人的使用情况
            if type(laonianyongyao) == float:
                laonianyongyao = ''
            laonianyongyao_split = laonianyongyao.split('；')
            try:
                laonianyongyao_list = [[ii.split('：')[0], ii.split('：')[1]] for ii in laonianyongyao_split if ii != '']
            except:
                print('cuowu', laonianyongyao, i)
                laonianyongyao_list = []
            for laonianyongyao_list_i in laonianyongyao_list:
                self.id_entity_relation_attribute.append([id, laonianyongyao_list_i[1], '老年用药', laonianyongyao_list_i[0]])



            funvyongyao = f['妇女标注_x'].loc[i]  # 每个药物的妇女用药情况
            if type(funvyongyao) == float:
                funvyongyao = ''
            funvyongyao_split = funvyongyao.split('；')
            try:
                funvyongyao_list = [[ii.split('：')[0], ii.split('：')[1]] for ii in funvyongyao_split if ii != '']
            except:
                print('cuowu', funvyongyao, i)
                funvyongyao_list = []
            for funvyongyao_list_i in funvyongyao_list:
                self.id_entity_relation_attribute.append([id, funvyongyao_list_i[1], '妇女用药', funvyongyao_list_i[0]])

    def create_kg(self):
        graph = Graph("http://localhost:7474", username="neo4j", password='123456')
        matcher = NodeMatcher(graph)
        graph.delete_all()

        for i in self.id_entity_relation_attribute:
            id_node = matcher.match('ID').where(name=str(i[0])).first()
            if id_node == None:
                id_node = Node('ID', name=str(i[0]))
                self.num_entity['ID'] += 1
                graph.create(id_node)

            entity = i[1]
            flag = 0
            for dict in self.dict_list:
                entity_change = entity.replace('-C','').replace('-P','') # 先将这些标签去掉，看看有没有，如果没有在下面在判断
                if entity_change == dict[0]:
                    flag = 1
                    entity_node = matcher.match( dict[1] ).where(name=str(entity)).first()
                    if entity_node == None:
                        entity_node = Node(dict[1], name=dict[0])
                        if dict[1] not in self.num_entity.keys():
                            self.num_entity[dict[1]] = 1
                        else:self.num_entity[dict[1]] +=1
                        graph.create(entity_node)
                    relation = Relationship(id_node,i[2],entity_node,property = i[3])
                    graph.create(relation)
                    if i[2] not in self.num_relation.keys():
                        self.num_relation[i[2]] =1
                    else:self.num_relation[i[2]] +=1
                    break

            if flag == 0 :
                if i[2] in ['儿童用药','老年用药','妇女用药']: # 在之前人群中没有出现过的和儿童妇女老人相关的描述，
                    entity_node = Node('病人属性',name = i[1])
                    self.num_entity['病人属性']+=1
                    graph.create(entity_node)
                    relation = Relationship(id_node,i[2],entity_node,property=i[3])
                    graph.create(relation)
                    if i[2] not in self.num_relation.keys():
                        self.num_relation[i[2]] =1
                    else:self.num_relation[i[2]] +=1

                elif '-P' in entity : # 标注过程中标记的病人标签
                    entity_node = matcher.match('病人属性').where(name=str( entity.replace('-P',''))).first()
                    if entity_node == None:
                        entity_node = Node('病人属性',name = entity.replace('-P','') )
                        if '病人属性' not in self.num_entity.keys():
                            self.num_entity['病人属性'] = 1
                        else:
                            self.num_entity['病人属性'] += 1

                    relation = Relationship(id_node,i[2],entity_node,property = i[3])
                    graph.create(relation)
                    if i[2] not in self.num_relation.keys():
                        self.num_relation[i[2]] =1
                    else:self.num_relation[i[2]] +=1

                elif '-C' in entity or i[2] == '包含': # 标记过程中标记的成份标签
                    entity_node = matcher.match( '西药成份').where(name=str(entity.replace('-C',''))).first()
                    if entity_node == None:
                        entity_node = Node('西药成份',name = entity.replace('-C',''))
                        if '西药成份' not in self.num_entity.keys():
                            self.num_entity['西药成份'] = 1
                        else:
                            self.num_entity['西药成份'] += 1

                    relation = Relationship(id_node,i[2],entity_node,property = i[3])
                    graph.create(relation)
                    if i[2] not in self.num_relation.keys():
                        self.num_relation[i[2]] =1
                    else:self.num_relation[i[2]] +=1

                elif i[2] == '治疗':
                    entity_node = matcher.match('症状').where(name =  entity).first()
                    if entity_node == None:
                        entity_node = Node('症状',name = entity)
                        if '症状' not in self.num_entity.keys():
                            self.num_entity['症状'] =1
                        else:
                            self.num_entity['症状'] +=1
                        relation = Relationship(id_node,'治疗',entity_node,property=i[3])
                        graph.create(relation)
                        if '治疗' not in self.num_relation.keys():
                            self.num_relation['治疗'] = 1
                        else:
                            self.num_relation['治疗'] +=1
                elif i[3] == '检查':
                    # 之前没有出现过的一次特殊的实体，例如 关系属性为 检查 时，实体对应的都是些体征和检查手段，在之前的字典中是没有的
                    entity_node = matcher.match('检查手段').where(name=str(entity)).first()
                    if entity_node == None:
                        entity_node = Node('检查手段', name=entity)
                        if '检查手段' not in self.num_entity.keys():
                            self.num_entity['检查手段'] = 1
                        else:
                            self.num_entity['检查手段'] += 1

                    if '检查手段' not in self.num_relation.keys():
                        self.num_relation[i[2]] = 1
                    else:
                        self.num_relation[i[2]] += 1
                    relation = Relationship(id_node, i[2], entity_node, property=i[3])
                    graph.create(relation)

                else:
                    # print('在字典中找不到实体分类',entity)
                    if entity not in self.wrong_entity:
                        self.wrong_entity.append(entity)






        zong = 0
        for i in self.num_entity.values():
            zong+=i
        print('在好心情知识图谱中实体共有{}个，具体数量如下\n实体|数量\n:-:|:-:'.format(zong))
        for k,v in self.num_entity.items():
            print(k,'|',v)
        print('\n')

        zong = 0
        for i in self.num_relation.values():
            zong+= i
        print('在好心情知识图谱中关系共有{}个，具体数量如下\n关系类别|数量\n:-:|:-:'.format(zong))
        for k,v in self.num_relation.items():
            print(k,'|',v)
        print('\n')





def run():


    zhongchengyaochengfen_add = '../data/dict/中成药成份.txt'
    xiyaochengfen_add = '../data/dict/西药成份.txt'
    bingrenshuxing_add = '../data/dict/病人属性.txt'
    jibing_add = '../data/dict/疾病.txt'
    zhengzhuang_add = '../data/dict/症状.txt'
    zhongyizhengxing_add = '../data/dict/中医证型.txt'


    haoxinqing = HaoXinQingKG()
    haoxinqing.add_dict(zhongchengyaochengfen_add, '中成药成份')
    haoxinqing.add_dict(xiyaochengfen_add, '西药成份')
    haoxinqing.add_dict(bingrenshuxing_add, '病人属性')
    haoxinqing.add_dict(jibing_add, '疾病')
    haoxinqing.add_dict(zhengzhuang_add, '症状')
    haoxinqing.add_dict(zhongyizhengxing_add, '中医证型')




    haoxinqing.get_data()
    haoxinqing.create_kg()

    with open('错误词.txt','w',encoding='utf-8') as f :
        f.write('\n'.join(haoxinqing.wrong_entity))


if __name__ == '__main__':
    run()