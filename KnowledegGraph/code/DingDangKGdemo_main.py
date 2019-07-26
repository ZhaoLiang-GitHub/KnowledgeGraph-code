from KnowledegGraph.code.add_taboo import add_taboo
from KnowledegGraph.code.neo4j import create_kg

if __name__ == '__main__':
    # 数据来源 1叮当实例文件 2寻医问药层级结构文件 3临床用药数据，构建知识图谱，在构建时会将之前的现有图谱清空
    create_kg()

    # 数据来源 1寻医问药中抽取的禁忌关系,在代码中修改是否添加实体，注释掉相关部分即可，默认是添加的
    add_taboo()
