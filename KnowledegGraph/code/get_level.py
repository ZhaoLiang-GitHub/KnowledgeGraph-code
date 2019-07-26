'''
将寻医问药四个分级文件与临床用药中的实体抽取出来并且直接放在neo4j数据库中，分级向量中，最后一个是具体的疾病，之前的是科室或者部位词
因为直接将实体存在了neo4j图数据中，所以在运行代码前连接到本地的图数据库，账目密码在set_config函数中进行修改
'''
from py2neo import Graph, Node, Relationship,NodeMatcher

def set_config():
    global xunyiwenyao_level,xunyiwenyao_node,linchuang_medicine_level,linchuang_medicine_node,entity_num,relation_num,buwei,keshi,graph,matcher
    graph = Graph("http://localhost:7474", username="neo4j", password='123456')
    matcher = NodeMatcher(graph)
    graph.delete_all()
    xunyiwenyao_level = [] #寻医问药中所有的层级结构，用来查询，不区分疾病和症状
    xunyiwenyao_node = [] #科室与部位的节点数据
    linchuang_medicine_level = []
    linchuang_medicine_node = []
    entity_num = {'科室':0,'部位':0,'临床分级':0}
    relation_num= {'包括':0}
    buwei = ['全身', '男性股沟', '颈部', '眼', '生殖部位', '下肢', '口', '上肢', '腰部', '耳', '四肢', '腹部', '头部', '皮肤', '女性盆骨', '排泄部位', '胸部', '皮肤', '鼻']
    keshi = ['眼科', '五官科', '皮肤科', '骨外科', '康复科', '中医骨伤科', '中医科', '耳鼻喉科', '理疗科', '体检科', '皮肤性病科', '泌尿内科', '遗传病科', '肝胆外科', '中西医结合科', '内科', '心胸外科', '肿瘤内科', '营养科', '药品科', '外科', '肛肠科', '神经内科', '烧伤科', '口腔科', '血液科', '小儿内科', '心理科', '神经外科', '泌尿外科', '肾内科', '消化内科', '肿瘤外科', '风湿免疫科', '呼吸内科', '普外科', '内分泌科', '妇产科', '妇科', '男科', '儿科综合', '精神科', '急诊科', '感染科', '其他科室', '传染科', '中医理疗科', '心内科', '小儿外科', '整形美容科', '儿科', '性病科', '产科', '肿瘤科',
             '生殖健康', '保健养生', '辅助检查', '重症监护', '其他综合', '中医综合', '不孕不育', '肝病', '减肥']

def get_depaetment_paert_from_xunyiwenyao():
    # 将寻医问药中的科室与部位结构抽取出来形成子图，在之后的疾病与症状中，查询该疾病或者症状在寻医问药中的层级结构中，在链接到最低的一个结构上
    with open('../data/xunyiwenyao/寻医问药--科室--疾病.txt','r',encoding='utf-8') as f:
        for i in f.readlines():
            List1 = i.strip().split('\t')[1].split('-->')
            List = [ii.lstrip('\"') for ii in List1 if ii != List1[-1] and ii != '']
            if List[0] not in xunyiwenyao_node:
                graph.create(Node('科室', name=List[0]))
                entity_num['科室']+=1
                xunyiwenyao_node.append(List[0])
            for j in range(1, len(List)):

                if List[j] not in xunyiwenyao_node:
                    this_node = Node('科室', name=List[j])
                    graph.create(this_node)
                    entity_num['科室'] += 1

                    xunyiwenyao_node.append(List[j])
                else:
                    this_node = matcher.match('科室').where(name=List[j]).first()
                front_node = matcher.match('科室').where(name=List[j - 1]).first()
                graph.create(Relationship(front_node, '包括', this_node))
                relation_num['包括']+=1

            List.append(List1[-1])
            xunyiwenyao_level.append(List)
    with open('../data/xunyiwenyao/寻医问药--科室--症状.txt','r',encoding='utf-8') as f:
        for i in f.readlines():
            List = i.strip().split('\t')[1].split('-->')
            List = [ii.lstrip('\"') for ii in List if ii!=List[-1] and ii!='']
            if List[0] not in xunyiwenyao_node:
                graph.create(Node('科室', name=List[0]))
                entity_num['科室'] += 1
                xunyiwenyao_node.append(List[0])
            for j in range(1, len(List)):

                if List[j] not in xunyiwenyao_node:
                    this_node = Node('科室', name=List[j])
                    entity_num['科室'] += 1
                    graph.create(this_node)
                    xunyiwenyao_node.append(List[j])
                else:
                    this_node = matcher.match('科室').where(name=List[j]).first()
                front_node = matcher.match('科室').where(name=List[j - 1]).first()
                graph.create(Relationship(front_node, '包括', this_node))
                relation_num['包括']+=1
            List.append(List1[-1])
            xunyiwenyao_level.append(List)
    with open('../data/xunyiwenyao/寻医问药--部位--疾病.txt','r',encoding='utf-8') as f:
        for i in f.readlines():
            List1 = i.strip().split('\t')[1].split('-->')
            List = [ii.strip() for ii in List1 if ii!=List1[-1] and ii!='']
            if List[0] not in xunyiwenyao_node:
                if List[0]  in keshi:
                    graph.create(Node('科室', name=List[0]))
                    entity_num['科室'] += 1
                elif List[0] in buwei:
                    graph.create(Node('部位',name = List[0]))
                    entity_num['部位'] +=1
                xunyiwenyao_node.append(List[0])
            for j in range(1, len(List)):

                if List[j] not in xunyiwenyao_node:
                    if List[j] in buwei:
                        this_node = Node('部位',name =List[j])
                        entity_num['部位']+=1
                        graph.create(this_node)
                        xunyiwenyao_node.append(List[j])
                    elif List[j] in keshi:
                        this_node = Node('科室',name =List[j])
                        entity_num['科室']+=1
                        graph.create(this_node)
                        xunyiwenyao_node.append(List[j])
                else:
                    if List[j] in buwei:
                        this_node = matcher.match('部位').where(name = List[j]).first()
                        if this_node ==None:
                            this_node = Node('部位', name=List[j])
                            entity_num['部位'] += 1
                            graph.create(this_node)
                            xunyiwenyao_node.append(List[j])

                    elif List[j]  in keshi:
                        this_node = matcher.match('科室').where(name = List[j]).first()

                if List[j-1] in buwei:
                    front_node = matcher.match('部位').where(name = List[j-1]).first()
                elif List[j-1] in keshi:
                    front_node = matcher.match('科室').where(name = List[j-1]).first()

                try:
                    graph.create(Relationship(front_node,'包括',this_node))
                    relation_num['包括']+=1
                except:
                    print(front_node,this_node)
            List.append(List1[-1])
            xunyiwenyao_level.append(List)

    with open('../data/xunyiwenyao/寻医问药--部位--症状.txt','r',encoding='utf-8') as f:
        for i in f.readlines():
            List1 = i.strip().split('\t')[1].split('-->')
            List = [ii.strip() for ii in List1 if ii!=List1[-1] and ii!='']
            if List[0] not in xunyiwenyao_node:
                if List[0] in keshi:
                    graph.create(Node('科室', name=List[0]))
                    entity_num['科室'] += 1
                elif List[0] in buwei:
                    graph.create(Node('部位',name = List[0]))
                xunyiwenyao_node.append(List[0])
            for j in range(1, len(List)):

                if List[j] not in xunyiwenyao_node:
                    if List[j] in buwei:
                        this_node = Node('部位',name =List[j])
                        entity_num['部位']+=1
                        graph.create(this_node)
                        xunyiwenyao_node.append(List[j])
                    elif List[j] in keshi:
                        this_node = Node('科室',name =List[j])
                        entity_num['科室']+=1
                        graph.create(this_node)
                        xunyiwenyao_node.append(List[j])

                else:
                    if List[j] in buwei:
                        this_node = matcher.match('部位').where(name = List[j]).first()
                    elif List[j] in keshi:
                        this_node = matcher.match('科室').where(name = List[j]).first()
                if List[j-1] in buwei:
                    front_node = matcher.match('部位').where(name = List[j-1]).first()
                elif List[j-1] in keshi:
                    front_node = matcher.match('科室').where(name = List[j-1]).first()

                graph.create(Relationship(front_node,'包括',this_node))
                relation_num['包括']+=1
            List.append(List1[-1])
            # if '脂肪肝' in ''.join(List):
            #     print(List1)

            xunyiwenyao_level.append(List)
    return xunyiwenyao_level, xunyiwenyao_node, graph

def get_medicine_level():
    # v1 得到临床药物手册中的药物分级结构，具体查看 临床药物手册_所有药物层级结构.txt
    # v2 将国家基本药物和临床用药中的抗微生物部分合并起来，具体查看 /原始数据/国家基本药物目录2018版/国家基本药物目录和临床药物手册中抗微生物药.txt

    with open('../data/medicine_level/国家基本药物目录和临床药物手册中抗微生物药.txt','r',encoding='utf-8') as f :
        for i in f.readlines():
            List1 = i.strip().split('->')
            List = [ii.lstrip('\"') for ii in List1 if ii != List1[-1] and ii != '']
            if List[0] not in linchuang_medicine_node:
                graph.create(Node('临床分级', name=List[0]))
                entity_num['临床分级'] += 1
                linchuang_medicine_node.append(List[0])
            for j in range(1, len(List)):

                if List[j] not in linchuang_medicine_node:
                    this_node = Node('临床分级', name=List[j])
                    entity_num['临床分级'] += 1
                    graph.create(this_node)
                    linchuang_medicine_node.append(List[j])
                else:
                    this_node = matcher.match('临床分级').where(name=List[j]).first()
                front_node = matcher.match('临床分级').where(name=List[j - 1]).first()
                graph.create(Relationship(front_node, '包括', this_node))
                relation_num['包括']+=1
            List.append(List1[-1])
            linchuang_medicine_level.append(List)
    return linchuang_medicine_level,linchuang_medicine_node,graph



def get_level():
    set_config()
    xunyiwenyao_level, xunyiwenyao_node, graph = get_depaetment_paert_from_xunyiwenyao()
    linchuang_medicine_level,linchuang_medicine_node,graph = get_medicine_level()
    with open('../生成文件/寻医问药中的科室部位层级结构.txt','w',encoding='utf-8') as f:
        for i in xunyiwenyao_level:
            f.write('-->'.join(i))
            f.write('\n')
    zong = 0
    for i in entity_num.values():
        zong+=i
    print('在寻医问药和临床药物手册中共有实体{}个，具体数量如下:\n实体类别|数量\n:-:|:-:'.format(zong))
    for k,v in entity_num.items():
        print(k,'|',v)
    print('\n')
    zong = 0
    for i in relation_num.values():
        zong+=i
    print('在寻医问药和临床药物手册中共有关系{}个，具体数量如下:\n关系类别|数量\n:-:|:-:'.format(zong))
    for k,v in relation_num.items():
        print(k,'|',v)
    print('\n')
    # print(linchuang_medicine_level)
    return xunyiwenyao_level, linchuang_medicine_level, graph

if __name__ =='__main__':
    get_level()
    # get_disease_symptom_level()