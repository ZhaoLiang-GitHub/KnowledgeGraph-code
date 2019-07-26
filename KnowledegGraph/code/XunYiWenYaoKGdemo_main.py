from py2neo import Graph, Node, Relationship,NodeMatcher
import pandas as pd
buwei = ['全身', '男性股沟', '颈部', '眼', '生殖部位', '下肢', '口', '上肢', '腰部', '耳', '四肢', '腹部', '头部', '皮肤', '女性盆骨', '排泄部位', '胸部', '皮肤', '鼻']
keshi = ['眼科', '五官科', '皮肤科', '骨外科', '康复科', '中医骨伤科', '中医科', '耳鼻喉科', '理疗科', '体检科', '皮肤性病科', '泌尿内科', '遗传病科', '肝胆外科', '中西医结合科', '内科', '心胸外科', '肿瘤内科', '营养科', '药品科', '外科', '肛肠科', '神经内科', '烧伤科', '口腔科', '血液科', '小儿内科', '心理科', '神经外科', '泌尿外科', '肾内科', '消化内科', '肿瘤外科', '风湿免疫科', '呼吸内科', '普外科', '内分泌科', '妇产科', '妇科', '男科', '儿科综合', '精神科', '急诊科', '感染科', '其他科室', '传染科', '中医理疗科', '心内科', '小儿外科', '整形美容科', '儿科', '性病科', '产科', '肿瘤科',
         '生殖健康', '保健养生', '辅助检查', '重症监护', '其他综合', '中医综合', '不孕不育', '肝病', '减肥']
entity_num = {'科室':0,'部位':0,'疾病':0,'症状':0,'中医证型':0,'中成药成份':0,'西药成份':0,'药品网页链接':0,'病人属性':0}
relation_num ={'包含':0,'治疗':0,'成份是':0,'禁忌':0,'导致':0}



def create_kg():
    graph = Graph("http://localhost:7474", username="neo4j", password='123456')
    matcher = NodeMatcher(graph)
    graph.delete_all()

    zhongchengyaochengfen = ''.join(open('../data/dict/中成药成份.txt','r',encoding='utf-8').readlines())
    xiyaochengfen = ''.join(open('../data/dict/西药成份.txt','r',encoding='utf-8').readlines())
    zhongyizhengxing = ''.join(open('../data/dict/中医证型.txt','r',encoding='utf-8').readlines())
    jibing = ''.join(open('../data/dict/疾病.txt','r',encoding='utf-8').readlines())
    zhengzhuang = ''.join(open('../data/dict/症状.txt','r',encoding='utf-8').readlines())
    department = open('../生成文件/寻医问药中的科室部位层级结构.txt','r',encoding='utf-8').readlines()


    xunyiwenyao_entity = pd.read_csv('../生成文件/寻医问药数据中抽取的实体.csv')
    for i in range(xunyiwenyao_entity.shape[0]):
        if xunyiwenyao_entity['类型'].loc[i] =='疾病':
            # 在抽取实体时，采用的是基于规则的方法，即在药品说明书中的某些字段内出现的实体被认为是疾病，在构建图谱时需要得到具体的实体类型
            if xunyiwenyao_entity['实体'].loc[i] in zhengzhuang:
                disease_node = Node('症状',name =xunyiwenyao_entity['实体'].loc[i])
                entity_num['症状'] +=1
            elif xunyiwenyao_entity['实体'].loc[i] in jibing:
                disease_node = Node('疾病',name =xunyiwenyao_entity['实体'].loc[i])
                entity_num['疾病'] +=1
            elif xunyiwenyao_entity['实体'].loc[i] in zhongyizhengxing:
                disease_node = Node('中医证型',name =xunyiwenyao_entity['实体'].loc[i])
                entity_num['中医证型'] +=1
            else:
                disease_node = Node('疾病',name =xunyiwenyao_entity['实体'].loc[i])
                entity_num['疾病'] +=1
            graph.create(disease_node)
            for j in department:
                if xunyiwenyao_entity['实体'].loc[i] in j :
                    List1 = j.strip().split('-->')
                    List = [ii.strip() for ii in List1 if ii != List1[-1] and ii != '']
                    for list_i in range(1,len(List)):
                        if List[list_i-1] in buwei:
                            front_node = matcher.match('部位').where(name = List[list_i-1]).first()
                            if front_node ==None:
                                front_node = Node('部位',name = List[list_i-1])
                                entity_num['部位']+=1
                                graph.create(front_node)
                        else:
                            front_node = matcher.match('科室').where(name = List[list_i-1]).first()
                            if front_node ==None:
                                front_node = Node('科室',name = List[list_i-1])
                                entity_num['科室']+=1
                                graph.create(front_node)

                        if List[list_i] in buwei:
                            this_node = matcher.match('部位').where(name = List[list_i]).first()
                            if this_node ==None:
                                this_node = Node('部位',name = List[list_i])
                                entity_num['部位']+=1
                                graph.create(this_node)
                        else:
                            this_node = matcher.match('科室').where(name = List[list_i]).first()
                            if this_node ==None:
                                this_node = Node('科室',name = List[list_i])
                                entity_num['科室']+=1
                                graph.create(this_node)

                        graph.create(Relationship(front_node,'包含',this_node))
                        relation_num['包含'] +=1
                    if List[-1] in buwei:
                        last_node = matcher.match('部位').where(name=List[-1]).first()
                        if last_node == None:
                            last_node = Node('部位',name = List[-1])
                            entity_num['部位'] += 1
                    else:
                        last_node = matcher.match('科室').where(name=List[-1]).first()
                        if last_node == None:
                            last_node = Node('科室',name = List[-1])
                        entity_num['科室'] += 1
                    graph.create(Relationship(last_node,'包含',disease_node))
                    relation_num['包含'] += 1

        elif xunyiwenyao_entity['类型'].loc[i] == '药品网页链接':
            graph.create(Node('药品网页链接', name = xunyiwenyao_entity['实体'].loc[i]))
            entity_num['药品网页链接'] +=1
        elif xunyiwenyao_entity['类型'].loc[i] == '成份':
            if  xunyiwenyao_entity['实体'].loc[i] in zhongchengyaochengfen:
                component_part_node = Node('中成药成份', name =xunyiwenyao_entity['实体'].loc[i])
                entity_num['中成药成份'] +=1
            elif xunyiwenyao_entity['实体'].loc[i] in xiyaochengfen:
                component_part_node = Node('西药成份', name =xunyiwenyao_entity['实体'].loc[i])
                entity_num['西药成份'] +=1
            graph.create(component_part_node)
    print('实体新建完成')


    xunyiwenyao_relationship = pd.read_csv('../生成文件/寻医问药中抽取关系.csv')
    for i in range(xunyiwenyao_relationship.shape[0]):
        if xunyiwenyao_relationship['关系类型'].loc[i] == '治疗' or \
                xunyiwenyao_relationship['关系类型'].loc[i] == '成份是':
            start_node = matcher.match(xunyiwenyao_relationship['开始节点类型'].loc[i]).where(name = xunyiwenyao_relationship['开始'].loc[i]).first()
            if start_node ==None:
                start_node = Node(xunyiwenyao_relationship['开始节点类型'].loc[i],name = xunyiwenyao_relationship['开始'].loc[i])
                graph.create(start_node)

            end_node = matcher.match(xunyiwenyao_relationship['结束节点类型'].loc[i]).where(name = xunyiwenyao_relationship['结束'].loc[i]).first()
            if end_node ==None:
                end_node = Node(xunyiwenyao_relationship['结束节点类型'].loc[i],name = xunyiwenyao_relationship['结束'].loc[i])
                graph.create(end_node)
            graph.create(Relationship(start_node,xunyiwenyao_relationship['关系类型'].loc[i],end_node))
            relation_num[xunyiwenyao_relationship['关系类型'].loc[i]]+=1
    print('治疗与成份关系添加完成')


    xunyiwenyao_tabbo = pd.read_csv('../生成文件/寻医问药数据中的禁忌关系.csv')
    for i in range(xunyiwenyao_tabbo.shape[0]):
        start_node = matcher.match('药品网页链接').where(name = xunyiwenyao_tabbo['开始'].loc[i]).first()
        end_node = matcher.match(xunyiwenyao_tabbo['节点类型'].loc[i]).where(name = xunyiwenyao_tabbo['结束'].loc[i]).first()
        if end_node == None:
            end_node = Node(xunyiwenyao_tabbo['节点类型'].loc[i],name = xunyiwenyao_tabbo['结束'].loc[i])
            entity_num[xunyiwenyao_tabbo['节点类型'].loc[i]]+=1
            graph.create(end_node)
        graph.create(Relationship(start_node,'禁忌',end_node))
        relation_num['禁忌'] += 1
    print('禁忌关系添加完成')


    symptom_lead_disease = open('../data/symptom_lead_disease/求医网中症状导致疾病层级结构.txt','r',encoding='utf-8')
    for i in symptom_lead_disease.readlines():
        disease = i.split('-导致-')[1]
        symptom = i.split('-导致-')[0]
        disease_node = matcher.match('疾病').where(name=disease).first()
        symptom_node = matcher.match('症状').where(name=symptom).first()
        if disease_node == None:
            disease_node = Node('疾病', name=disease)
            graph.create(disease_node)
            entity_num['疾病']+=1
        if symptom_node == None:
            symptom_node = Node('症状', name=disease)
            graph.create(symptom_node)
            entity_num['症状']+=1
        graph.create(Relationship(symptom_node, '导致', disease_node))
        relation_num['导致'] +=1
    print('添加症状-疾病之间的层级结构关系')



    zong = 0
    for i in relation_num.values():
        zong+=i
    print('在寻医问药知识图谱中共有关系{}个，具体数量如下:\n关系类别|数量\n:-:|:-:'.format(zong))
    for k,v in relation_num.items():
        print(k,'|',v)
    print('\n')

    zong = 0
    for i in entity_num.values():
        zong+=i
    print('在寻医问药知识图谱中共有实体{}个具体数目如下:\n实体类型|数量\n:-:|:-:'.format(zong))
    for k,v in entity_num.items():
        print(k,'|',v)
    print('\n')


if __name__ =='__main__':
    create_kg()