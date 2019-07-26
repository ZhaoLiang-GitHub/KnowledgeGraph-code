# -*- coding: utf-8 -*-
# @Author: zhaoliang
# @Date:   2019-07-11 14:40:06
# @Email:  1318525510@qq.com
# @Last Modified by:   admin
# @Last Modified time: 2019-07-18 15:56:02

'''
将从寻医问药数据中得到的禁忌关系添加到叮当快药KGdemo中
'''
from py2neo import Graph, Node, Relationship,NodeMatcher
import pandas as pd
import re

def add_taboo():
    dingdang_taboo_file = open('../生成文件/叮当快药中的存在的禁忌关系.txt','a',encoding='utf-8')
    dingdang_taboo_file.seek(0)
    dingdang_taboo_file.truncate()#清空文件
    dingdang_taboo_file.write('\t'.join(['SKU','药品名称','关系','禁忌实体','\n']))
    dingdang_taboo_list = []
    graph = Graph("http://localhost:7474", username="neo4j", password='123456')
    matcher = NodeMatcher(graph)
    f_xunyiwenyao = pd.read_csv('../data/xunyiwenyao/寻医问药中药品名的禁忌关系.csv', encoding='utf-8')
    f_dingdang = pd.read_excel('../data/dingdangkuaiyao/与创新工场共创知识图谱的试实验数据.xlsx')
    yaopingming_xunyiwenyao = list(f_xunyiwenyao['药品名'])
    tongyongmingcheng_dingdang = list(f_dingdang['通用名称'])

    shangpinmingcheng_dingdang = []
    for i in list(f_dingdang['商品名称']):
        ii = re.sub(pattern='\[.*\]', string=i, repl='')
        iii = re.sub(pattern=r'[(](.*)[)]', string=ii, repl='')
        iiii = re.sub(pattern=r'（.*）', string=iii, repl='')
        shangpinmingcheng_dingdang.append(iiii)

    jinji_chonghe = []
    for i in list(set(yaopingming_xunyiwenyao) & set(tongyongmingcheng_dingdang)):
        jinji_chonghe.append(i)
    for i in list(set(shangpinmingcheng_dingdang) & set(yaopingming_xunyiwenyao)):
        jinji_chonghe.append(i)

    buchongfu_jishu = 0
    weichuxian= []
    for i in range(f_dingdang.shape[0]):
        a = f_dingdang['商品名称'].loc[i]
        a = re.sub(pattern='\[.*\]', string=a, repl='')
        a = re.sub(pattern=r'[(](.*)[)]', string=a, repl='')
        a = re.sub(pattern=r'（.*）', string=a, repl='')

        if a not in jinji_chonghe and f_dingdang['通用名称'].loc[i] not in jinji_chonghe:
            buchongfu_jishu += 1
            weichuxian.append(f_dingdang.loc[i])
            # print(f_dingdang.loc[i])
    weichuxian = pd.DataFrame(weichuxian)
    weichuxian.to_csv('../生成文件/叮当快药数据中不存在禁忌关系的药物集合.csv',index=False)

    print('叮当快药实例数据中共有药物{}个，基于寻医问药数据共有{}个药物添加禁忌关系，占总数量的{}%'
          .format(len(tongyongmingcheng_dingdang), buchongfu_jishu,str( 100*buchongfu_jishu/len(tongyongmingcheng_dingdang) )[:4] ))
    # print('叮当快药实例数据中共有以通用名称或商品名称为唯一主键的不重复药物{}个，基于寻医问药数据共有{}个药物添加禁忌关系，占总数量的{}%'
    #       .format(len(set(tongyongmingcheng_dingdang)),len(set(jinji_chonghe)),len(set(jinji_chonghe))/len(set(tongyongmingcheng_dingdang))))

    jinji_list = []
    for i in range(f_dingdang.shape[0]):
        if f_dingdang['通用名称'].loc[i] in jinji_chonghe:
            jinji_list.append([f_dingdang['商品SKU编码'].loc[i], f_dingdang['通用名称'].loc[i]])
        elif f_dingdang['商品名称'].loc[i] in jinji_chonghe:
            jinji_list.append([f_dingdang['商品SKU编码'].loc[i], f_dingdang['商品名称'].loc[i]])

    jinji_num = {'药物-禁忌-病人': 0, '药物-禁忌-药物': 0, '药物-禁忌-疾病或病症': 0, '药物-禁忌-成份': 0}
    new_entiyt = {'病症':0,'病人属性':0,'成份':0,'禁忌相关药物':0}
    for i in range(f_xunyiwenyao.shape[0]):
        for jinji in jinji_list:
            if f_xunyiwenyao['药品名'].loc[i] == jinji[1]:
                start_node = matcher.match('商品SKU编码').where(name=str(jinji[0])).first()
                if start_node ==None:
                    start_node = Node('商品SKU编码',name = str(jinji[0]))
                label = f_xunyiwenyao['节点类型'].loc[i]
                if label == '疾病或病症':
                    print(1)
                    end_node1 = matcher.match('疾病').where(name=f_xunyiwenyao['禁忌节点'].loc[i]).first()
                    end_node2 = matcher.match('病症').where(name=f_xunyiwenyao['禁忌节点'].loc[i]).first()
                    if end_node1 != None:
                        if ''.join([dict(start_node)['name'],'\t','禁忌','\t',dict(end_node1)['name'],'\n']) not in dingdang_taboo_list:
                            jinji_num['药物-禁忌-疾病或病症'] += 1
                            graph.create(Relationship(start_node, '禁忌', end_node1))
                            dingdang_taboo_file.write(''.join([dict(start_node)['name'],'\t',jinji[1],'\t','禁忌','\t',dict(end_node1)['name'],'\n']))
                            dingdang_taboo_list.append(''.join([dict(start_node)['name'],'\t','禁忌','\t',dict(end_node1)['name'],'\n']))
                    if end_node2 != None:
                        if ''.join([dict(start_node)['name'],'\t','禁忌','\t',dict(end_node2)['name'],'\n']) not in dingdang_taboo_list:
                            jinji_num['药物-禁忌-疾病或病症'] += 1
                            graph.create(Relationship(start_node, '禁忌', end_node2))
                            dingdang_taboo_file.write(''.join([dict(start_node)['name'],'\t',jinji[1],'\t','禁忌','\t',dict(end_node2)['name'],'\n']))
                            dingdang_taboo_list.append(''.join([dict(start_node)['name'],'\t','禁忌','\t',dict(end_node2)['name'],'\n']))
                    if end_node2 == None and end_node1 == None:
                        end_node = Node('病症', name=f_xunyiwenyao['禁忌节点'].loc[i])  # 如果在寻医问药中的疾病或病症数据没有在叮当中出现，统一设置为病症
                        new_entiyt['病症'] +=1

                        if ''.join([dict(start_node)['name'],'\t','禁忌','\t',dict(end_node)['name'],'\n']) not in dingdang_taboo_list:
                            jinji_num['药物-禁忌-疾病或病症'] += 1
                            graph.create(Relationship(start_node, '禁忌', end_node))
                            dingdang_taboo_file.write(''.join([dict(start_node)['name'],'\t',jinji[1],'\t','禁忌','\t',dict(end_node)['name'],'\n']))
                            dingdang_taboo_list.append(''.join([dict(start_node)['name'],'\t','禁忌','\t',dict(end_node)['name'],'\n']))



                elif label == '病人属性':
                    end_node = matcher.match('病人属性').where(name=f_xunyiwenyao['禁忌节点'].loc[i]).first()
                    if end_node == None:
                        end_node = Node('病人属性', name=f_xunyiwenyao['禁忌节点'].loc[i])
                        new_entiyt['病人属性'] += 1
                    if ''.join([dict(start_node)['name'], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']) not in dingdang_taboo_list:
                        jinji_num['药物-禁忌-病人'] += 1
                        graph.create(Relationship(start_node, '禁忌', end_node))
                        dingdang_taboo_file.write(''.join([dict(start_node)['name'], '\t',jinji[1], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']))
                        dingdang_taboo_list.append(''.join([dict(start_node)['name'], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']))


                elif label == '成份':
                    end_node = matcher.match('成份').where(name=f_xunyiwenyao['禁忌节点'].loc[i]).first()
                    if end_node == None:
                        end_node = Node('成份', name=f_xunyiwenyao['禁忌节点'].loc[i])
                        new_entiyt['成份'] += 1
                        if ''.join([dict(start_node)['name'], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']) not in dingdang_taboo_list:
                            jinji_num['药物-禁忌-成份'] += 1
                            graph.create(Relationship(start_node, '禁忌', end_node))
                            dingdang_taboo_file.write(''.join([dict(start_node)['name'],'\t',jinji[1], '\t','禁忌','\t',dict(end_node)['name'],'\n']))
                            dingdang_taboo_list.append(''.join([dict(start_node)['name'], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']))

                    if end_node != None:
                        if ''.join([dict(start_node)['name'], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']) not in dingdang_taboo_list:
                            jinji_num['药物-禁忌-成份'] += 1
                            graph.create(Relationship(start_node, '禁忌', end_node))
                            dingdang_taboo_file.write(''.join([dict(start_node)['name'],'\t',jinji[1],'\t','禁忌','\t',dict(end_node)['name'],'\n']))
                            dingdang_taboo_list.append(''.join([dict(start_node)['name'], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']))



                elif label == '药物':
                    end_name = f_xunyiwenyao['禁忌节点'].loc[i]
                    print('禁忌药物名称',end_name)
                    if end_name in tongyongmingcheng_dingdang:
                        sku = f_dingdang.loc[f_dingdang['通用名称'] == end_name]['商品SKU编码'].tolist()[0]
                        end_node = matcher.match('商品SKU编码').where(name=sku).first()
                        if ''.join([dict(start_node)['name'], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']) not in dingdang_taboo_list:
                            graph.create(Relationship(start_node, '禁忌', end_node))
                            dingdang_taboo_file.write(''.join([dict(start_node)['name'],'\t',jinji[1],'\t','禁忌','\t',dict(end_node)['name'],'\n']))
                            jinji_num['药物-禁忌-药物'] += 1
                            dingdang_taboo_list.append(''.join([dict(start_node)['name'], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']))
                    elif end_name in shangpinmingcheng_dingdang:
                        sku = f_dingdang.loc[f_dingdang['商品名称'] == end_name]['商品SKU编码'].tolist()[0]
                        end_node = matcher.match('商品SKU编码').where(name=sku).first()
                        if ''.join([dict(start_node)['name'], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']) not in dingdang_taboo_list:
                            graph.create(Relationship(start_node, '禁忌', end_node))
                            dingdang_taboo_file.write(''.join([dict(start_node)['name'],'\t',jinji[1],'\t','禁忌','\t',dict(end_node)['name'],'\n']))
                            jinji_num['药物-禁忌-药物'] += 1
                            dingdang_taboo_list.append(''.join([dict(start_node)['name'], '\t', '禁忌', '\t', dict(end_node)['name'], '\n']))
                    else:
                        print(f_xunyiwenyao['节点类型'].loc[i], '中的禁忌药物不在叮当快药数据中')
                        pass


    zong_num = 0
    for i in jinji_num.values():
        zong_num += i
    print('在叮当快药知识图谱demo中添加了寻医问药数据中相关的{}条禁忌关系,具体的数量如下：\n关系类别|数量\n:-:|:-:'.format(zong_num))
    for k, v in jinji_num.items():
        print(k, '|', v)
    print('\n')

    zong_num = 0
    for i in new_entiyt.values():
        zong_num+=i
    print('在叮当快药知识图谱demo中添加了寻医问药数据禁忌关系中相关的{}个实体,具体的数量如下:\n实体类别|数量\n:-:|:-:'.format(zong_num))
    for k,v in new_entiyt.items():
        print(k,'|',v)
    print('\n')

if __name__ == '__main__':
    add_taboo()
