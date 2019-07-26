from py2neo import Graph, Node, Relationship,NodeMatcher

class GRAPH(object):
    '''
    构建neo4j知识图谱的类
    '''

    def __init__(self, dataframe, url, username, password):
        self.graph = Graph(url=url, username=username, password=password)
        self.matcher = NodeMatcher(self.graph)
        self.node_labels_dict = {}
        self.node_list = []
        self.relationship_dict = {}
        self.relationship_list = []
        self.dict_list = [] #所有的输入字典，每一个元素[实体,实体类别]
        self.dataframe = dataframe # 输入的dataframe对象
        self.data_all_entity = [] # 抽取出来的实体，每一行是一个字典
        # self.all_label = []
        self.all_medicine_name = [] #在数据中出现过的所有药物名字，在原始数据中的"药物名字"列有厂家名，在这里去掉了


    def create_node(self, ):
        '''
        每一个实体[实体名,实体类别]构建neo4j的唯一实体，
        :return:
        '''
        for line in self.data_all_entity:
            for key, value in line.items():
                if key not in self.node_labels_dict:
                    self.node_labels_dict[key] = 0

                if key not in self.node_list:
                    self.node_labels_dict[key] = 1
                    if type(value) != list and value != '':
                        self.graph.create(Node(key, name=value))
                        self.node_list.append(value)
                    elif type(value) == list:
                        for i in value:
                            self.graph.create(Node(key, name=i))
                            self.node_list.append(i)

    def show_information_entity_ralationgship(self):
        print('共有实体{}类,其中的具体数目是：'.format(len(self.node_labels_dict.keys())))
        for i in self.node_labels_dict.keys():
            print('{}\t{}'.format(i, self.node_labels_dict[i]))
        # self.coverage_rate()
        print('共有关系{}类,其中的具体数目是'.format(len(self.relationship_dict), ))
        for key in self.relationship_dict.keys():
            print('{}\t{}'.format(key, self.relationship_dict[key]))

    def coverage_rate(self):
        '''
        计算输入字典的对于药物抽取实体的覆盖程度
        抽取出来的实体中，成分实体 对应着 药物所有成份，相关疾病和疾病与症状 对应着 疾病或症状
        :return:
        '''
        disease_symptom_entity = []
        compment_entity = []
        for line in self.data_all_entity:
            disease_symptom_entity = line['相关疾病']
            for i in line:
                if i[1] == '疾病' or i[1] == '疾病或症状':
                    disease_symptom_entity.append(i[0])
                if i[1] == '成份':
                    compment_entity.append(i[0])
        disease_symptom_dict = []
        compment_dict = []
        for j in self.dict_list:
            if j[1] == '疾病或症状':
                disease_symptom_dict.extend(j[0])
            elif j[1] == '成份':
                compment_dict.extend(j[0])

        # print('在数据中共抽取出疾病&症状实体{}个,在加入的字典中共有症状&疾病{}个'.format(len(set(disease_symptom_entity)),len(disease_symptom_dict)))
        # print('数据中抽取出来的实体被症状字典覆盖的比例为{}%'.format(1-len(set(disease_symptom_entity)-(set(disease_symptom_entity)&set(disease_symptom_dict)))/len(set(disease_symptom_entity))))
        with open('在字典中没有被记录的疾病或症状.txt', 'w', encoding='utf-8') as f:
            # 将那些没有被记录在字典中症状或疾病记录下来，并添加在症状字典中
            for i in set(disease_symptom_entity) - (set(disease_symptom_entity) & set(disease_symptom_dict)):
                f.writelines(i + '\n')
        for j in self.dict_list:
            if j[1] == '疾病或症状':
                for k in set(disease_symptom_entity) - (set(disease_symptom_entity) & set(disease_symptom_dict)):
                    j[0].append([k, j[1]])

        print('在数据中共抽取出成份实体{}个，在加入的字典中共有成份{}个'.format(len(set(compment_entity)), len(compment_dict)))
        print('成份由成份字典匹配得到所以成份被覆盖率为100%')
        # print('在数据中抽取出来的成份被成份字典覆盖的比例为{}%'.format(1-len(set(compment_entity)-(set(compment_entity)&set(compment_dict)))/len(set(compment_entity))))

    def create_relationship(self, start='', relationgship='', end=''):
        for line in self.data_all_entity:
            start_node_list = []
            end_node_list = []
            if line[start] == None or line[end] == None:
                break
            else:
                if type(line[start]) != list:
                    start_node = self.matcher.match(start).where(name=line[start]).first()
                    start_node_list.append(start_node)
                else:
                    for start_node_i in line[start]:
                        start_node_list.append(self.matcher.match(start).where(name=line[start][start_node_i]).first())
                if type(line[end]) != list:
                    end_node = self.matcher.match(end).where(name=line[end]).first()
                    end_node_list.append(end_node)
                else:
                    for end_node_i in line[end]:
                        end_node_list.append(self.matcher.match(start).where(name=line[start][end_node_i]).first())
                for start_node_list_i in start_node_list:
                    for end_node_list_i in end_node_list:
                        self.graph.create(Relationship(start_node_list_i, relationgship, end_node_list_i))
                        if relationgship not in self.relationship_dict.keys():
                            self.relationship_dict[relationgship] = 1
                        else:
                            self.relationship_dict[relationgship] += 1

    def get_write_tabbo_relation(self, start_name, start_label, relation, end_name, end_lable):
        start_node = self.matcher.match(start_label).where(name=start_name).first()
        if start_node == None:
            start_node = Node(start_label, name=start_name)
            self.graph.create(start_node)
        end_node = self.matcher.match(end_lable).where(name=end_name).first()
        if end_node == None:
            end_node = Node(end_lable, name=end_name)
            self.graph.create(end_node)
        self.graph.create(Relationship(start_node, relation, end_node))

        if relation not in self.relationship_dict.keys():
            self.relationship_dict[relation] = 1
        else:
            self.relationship_dict[relation] += 1

def run():
    graph =GRAPH()
