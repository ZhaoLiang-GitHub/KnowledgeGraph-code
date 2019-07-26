from py2neo import Graph, Node, Relationship,NodeMatcher
import pandas as pd
import re
buwei = ['全身', '男性股沟', '颈部', '眼', '生殖部位', '下肢', '口', '上肢', '腰部', '耳', '四肢', '腹部', '头部', '皮肤', '女性盆骨', '排泄部位', '胸部', '皮肤', '鼻']
keshi = ['眼科', '五官科', '皮肤科', '骨外科', '康复科', '中医骨伤科', '中医科', '耳鼻喉科', '理疗科', '体检科', '皮肤性病科', '泌尿内科', '遗传病科', '肝胆外科', '中西医结合科', '内科', '心胸外科', '肿瘤内科', '营养科', '药品科', '外科', '肛肠科', '神经内科', '烧伤科', '口腔科', '血液科', '小儿内科', '心理科', '神经外科', '泌尿外科', '肾内科', '消化内科', '肿瘤外科', '风湿免疫科', '呼吸内科', '普外科', '内分泌科', '妇产科', '妇科', '男科', '儿科综合', '精神科', '急诊科', '感染科', '其他科室', '传染科', '中医理疗科', '心内科', '小儿外科', '整形美容科', '儿科', '性病科', '产科', '肿瘤科',
         '生殖健康', '保健养生', '辅助检查', '重症监护', '其他综合', '中医综合', '不孕不育', '肝病', '减肥']
buwei_show_list = []
keshi_show_list = []
linchuang_show_list = []

from KnowledegGraph.code.get_level import get_level

def create_kg():
    graph = Graph("http://localhost:7474", username="neo4j", password='123456')
    matcher = NodeMatcher(graph)
    graph.delete_all()

    skus = []  # SKU码，
    trade_names = []  # 商品名称，
    generic_names = []  # 通用名称
    specifications = []  # 药物规格，药物规格没有做处理是字符串
    first_commoditys = []  # 药物一级分类
    second_commoditys = []  # 药物二级分类
    third_commoditys = []  # 药物三级分类
    OTC_labels = []  # OTC标识分类
    medicine_classifications = []  # 药物分类
    diseases = []  # 疾病
    symptoms = []  # 病症
    components = []  # 药物成份
    entity_num ={
        '商品SKU编码':0,'商品名称':0,'通用名称':0,'规格':0,'商品一级分类':0,'商品二级分类':0,'商品三级分类':0,'OTC标识分类':0,'药物分类':0,'疾病':0,'病症':0,'成份':0,

    }
    relationgship_num ={
        '商品名称是':0,'通用名称是':0,'规格是':0,'包括':0,'治疗':0,'导致':0,'包含':0
    }
    xunyiwenyao_entity ={
        '科室':0,'部位':0,'临床分级':0
    }
    xunyiwenyao_level, linchuang_medicine_level, graph = get_level()

    data = pd.read_excel('../data/dingdangkuaiyao/与创新工场共创知识图谱的试实验数据.xlsx')
    # 商品SKU编码	商品名称	通用名称	规格	商品一级分类	商品二级分类	商品三级分类	OTC标识	分类	疾病	病症	成份

    for i in range(data.shape[0]):
        sku = str(data['商品SKU编码'].loc[i])
        if sku not in skus:
            sku_node = Node('SKU', name=sku)
            graph.create(sku_node)
            entity_num['商品SKU编码']+=1
            skus.append(sku)
        else:
            sku_node = matcher.match("SKU").where(name=sku).first()

        trade_name = str(data['商品名称'].loc[i])
        if trade_name not in trade_names:
            trade_name_node = Node('商品名称', name=trade_name)
            graph.create(trade_name_node)
            entity_num['商品名称']+=1
            trade_names.append(trade_name)
        else:
            trade_name_node = matcher.match("商品名称").where(name=trade_name).first()
        # for medicine_name in linchuang_medicine_level:
        # if trade_name in medicine_name:
        #     print(trade_name,medicine_name)

        graph.create(Relationship(sku_node, '商品名称是', trade_name_node))
        relationgship_num['商品名称是']+=1

        generic_name = str(data['通用名称'].loc[i])
        if generic_name not in generic_names:
            generic_name_node = Node('通用名称', name=generic_name)
            graph.create(generic_name_node)
            entity_num['通用名称']+=1
            generic_names.append(generic_name)
        else:
            generic_name_node = matcher.match('通用名称').where(name=generic_name).first()



        graph.create(Relationship(sku_node, '通用名称是', generic_name_node))
        relationgship_num['通用名称是']+=1

        specification = str(data['规格'].loc[i])
        if specification not in specifications:
            specification_node = Node('规格', name=specification)
            graph.create(specification_node)
            entity_num['规格']+=1
            specifications.append(specification)
        else:
            specification_node = matcher.match('规格').where(name=specification).first()
        graph.create(Relationship(sku_node, '规格是', specification_node))
        relationgship_num['规格是']+=1

        first_commodity = str(data['商品一级分类'].loc[i])
        if first_commodity not in first_commoditys:
            first_commodity_node = Node('商品一级分类', name=first_commodity)
            entity_num['商品一级分类']+=1
            graph.create(first_commodity_node)
            first_commoditys.append(first_commodity)
        else:
            first_commodity_node = matcher.match('商品一级分类').where(name=first_commodity).first()

        second_commodity = str(data['商品二级分类'].loc[i])
        if second_commodity not in second_commoditys:
            second_commodity_node = Node('商品二级分类', name=second_commodity)
            entity_num['商品二级分类']+=1
            graph.create(second_commodity_node)
            second_commoditys.append(second_commodity)
            graph.create(Relationship(first_commodity_node, '包括', second_commodity_node))
            relationgship_num['包括']+=1
        else:
            second_commodity_node = matcher.match('商品二级分类').where(name=second_commodity).first()

        third_commodity = str(data['商品三级分类'].loc[i])
        if third_commodity not in third_commoditys:
            third_commodity_node = Node('商品三级分类', name=third_commodity)
            entity_num['商品三级分类']+=1
            graph.create(third_commodity_node)
            third_commoditys.append(third_commodity)
            graph.create(Relationship(second_commodity_node, '包括', third_commodity_node))
            relationgship_num['包括']+=1
        else:
            third_commodity_node = matcher.match('商品三级分类').where(name=third_commodity).first()
        graph.create(Relationship(third_commodity_node, '包括', sku_node))
        relationgship_num['包括']+=1

        OTC_label = str(data['OTC标识'].loc[i])
        if OTC_label not in OTC_labels:
            OTC_label_node = Node('OTC标识分类', name=OTC_label)
            entity_num['OTC标识分类']+=1
            graph.create(OTC_label_node)
            OTC_labels.append(OTC_label)
        else:
            OTC_label_node = matcher.match('OTC标识分类').where(name=OTC_label).first()
        graph.create(Relationship(OTC_label_node, '包括', sku_node))
        relationgship_num['包括']+=1

        medicine_classification = str(data['分类'].loc[i])
        if medicine_classification not in medicine_classifications:
            medicine_classification_node = Node('药物分类', name=medicine_classification)
            entity_num['药物分类']+=1
            graph.create(medicine_classification_node)
            medicine_classifications.append(medicine_classification)
        else:
            medicine_classification_node = matcher.match('药物分类').where(name=medicine_classification).first()
        graph.create(Relationship(medicine_classification_node, '包括', sku_node))
        relationgship_num['包括']+=1

        disease_list = str(data['疾病'].loc[i])
        disease_list = re.split(pattern='，|,', string=disease_list)
        for disease in disease_list:
            if disease not in diseases:
                disease_node = Node('疾病', name=disease)
                graph.create(disease_node)
                entity_num['疾病']+=1
                diseases.append(disease)
            else:
                disease_node = matcher.match('疾病').where(name=disease).first()
            graph.create(Relationship(sku_node, '治疗', disease_node))
            relationgship_num['治疗']+=1
            for j in xunyiwenyao_level:
                if disease == j[-1]:
                    # print('疾病分级',disease)
                    if j[-2] in keshi :
                        disease_frot1 = matcher.match('科室').where(name=j[-2]).first()
                        graph.create(Relationship(disease_frot1, '包括', disease_node))
                        relationgship_num['包括']+=1
                        if j[-2] not in keshi_show_list:
                            xunyiwenyao_entity['科室']+=1
                            keshi_show_list.append(j[-2])
                    elif j[-2] in buwei:
                        disease_frot2 = matcher.match('部位').where(name=j[-2]).first()
                        graph.create(Relationship(disease_frot2, '包括', disease_node))
                        relationgship_num['包括']+=1
                        if j[-2] not in buwei_show_list:
                            xunyiwenyao_entity['部位']+=1
                            buwei_show_list.append(j[-2])




        symptom_list = str(data['病症'].loc[i])
        symptom_list = re.split(pattern='，|,', string=symptom_list)
        for symptom in symptom_list:
            if symptom not in symptoms:
                symptom_node = Node('病症', name=symptom.strip())
                entity_num['病症']+=1
                graph.create(symptom_node)
                symptoms.append(symptom)
            else:
                symptom_node = matcher.match('病症').where(name=symptom).first()
            try:
                graph.create(Relationship(sku_node, '治疗', symptom_node))
                relationgship_num['治疗']+=1
            except:
                print(sku_node,symptom_node)
            for j in xunyiwenyao_level:
                if symptom == j[-1]:
                    # print(symptom)
                    disease_frot1 = matcher.match('科室').where(name=j[-2]).first()
                    disease_frot2 = matcher.match('部位').where(name=j[-2]).first()
                    if disease_frot1 != None:
                        graph.create(Relationship(disease_frot1, '包括', symptom_node))
                        relationgship_num['包括']+=1
                        if j[-2] not in keshi_show_list:
                            xunyiwenyao_entity['科室']+=1
                            keshi_show_list.append(j[-2])
                    if disease_frot2 != None:
                        graph.create(Relationship(disease_frot2, '包括', symptom_node))
                        relationgship_num['包括']+=1
                        if j[-2] not in buwei_show_list:
                            xunyiwenyao_entity['部位']+=1
                            buwei_show_list.append(j[-2])
        for medicine_name in linchuang_medicine_level:
            if generic_name in medicine_name:
                medicine_name_node = matcher.match('临床分级').where(name=medicine_name[-2])
                if medicine_name[-2] not in linchuang_show_list:
                    xunyiwenyao_entity['临床分级'] +=1
                    linchuang_show_list.append(medicine_name[-2])
                graph.create(Relationship(medicine_name_node, '包含', sku_node))
                relationgship_num['包含']+=1
                # print(generic_name,medicine_name)





        component_list = str(data['成份'].loc[i]).strip()
        component_list = re.split(pattern='，|,', string=component_list)
        for component in component_list:
            if component not in components:
                component_node = Node('成份', name=component)
                entity_num['成份']+=1
                graph.create(component_node)
                components.append(component)
            else:
                component_node = matcher.match('成份').where(name=component).first()
            graph.create(Relationship(sku_node, '包含', component_node))
            relationgship_num['包括']+=1

        for disease in disease_list:
            disease_node = matcher.match('疾病').where(name=disease).first()
            for symptom in symptom_list:
                symptom_node = matcher.match('病症').where(name=symptom).first()
                if symptom_node ==None:
                    symptom_node = Node('病症',name = symptom)
                    graph.create(symptom_node)
                try:
                    graph.create(Relationship(symptom_node, '导致', disease_node))
                    relationgship_num['导致']+=1
                except:
                    print(symptom_node,disease_node)


    zong = 0
    for i in entity_num.values():
        zong+=i
    print('在叮当快药知识图谱demo中共有实体{}个，具体数量如下：\n实体类别|数量\n:-:|:-:'.format(zong))
    for k,v in entity_num.items():
        print(k,'|',v)
    print('\n')

    zong = 0
    for i in xunyiwenyao_entity.values():
        zong+=i
    print('在叮当快药知识图谱中添加了来自寻医问药与临床药物手册中的相关实体共有{}个，具体数量如下：'.format(zong))
    for k,v in xunyiwenyao_entity.items():
        print(k,'|',v)


    zong = 0
    for i in relationgship_num.values():
        zong+=1
    print('在叮当快药知识图谱demo中共有关系{}类，具体数量如下\n关系类别|数量\n:-:|:-:'.format(zong))
    for k,v in relationgship_num.items():
        print(k,'|',v)
    print('\n')






if __name__ =='__main__':
    create_kg()



