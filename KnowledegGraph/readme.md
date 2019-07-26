叮当快药知识图谱demo
1. 数据来源
    1. 与创新工场共创知识图谱的试实验数据.xlsx 
    2. 寻医问药中药品名的禁忌关系.csv
    3. 寻医问药--科室--疾病.txt
    4. 寻医问药--科室--症状.txt
    5. 寻医问药--部位--疾病.txt
    6. 寻医问药--部位--症状.txt
    7. 临床药物手册_所有药物层级结构.txt

2. 数据意义

    1. 为叮当快药提供的实例数据
    3. 寻医问药数据中提取的所有禁忌关系
    4. 3-6 为寻医问药网站中的科室、部位与症状、疾病的层级结构
    5. 7为临床药物手册中提到的药物层级结构

3. 代码
    
    1. 在命令行内输入

        cd ****/neo4j-community-3.5.5/bin
        
        ./neo4j start

    启动neo4j数据库，在第一次登陆时会提醒修改用户名密码，初始默认用户名密码均是neo4j，修改摩玛之后在neo4j.py文件中修改对应的用户名与密码，代码中使用的用户名是"neo4j" ，密码是"123456"
    
    2. 运行 DingDangKGdemo_main.py 文件
    3. 刷新 http://localhost:7474 网页即可
    
4. 代码逻辑

    1. 在get_level.py文件中，将寻医问药四个文件与临床数据中的层级结构拿出来，放在了neo4j的数据库里，将
 寻医问药中的层级结构保存下来，方法就是看每一个实体在图谱中是否出现，如果没有就新建，有的话去匹配，并且去找打对应的层级结构并导入在neo4j中
 
    2. 在neo4j.py文件中，将订单快药的实例数据分别抽取出来，并构建实体导入neo4j数据库中，方法是如果没有就新建，如果存在就查询找到并构建关系，关系在数据中的知识图谱.jpg中
    3. 在add_taboo.py 文件中，数据是之前抽取的
    
5. 数据库的导入导出

    1. 导出数据库
        
        cd ****/neo4j-community-3.5.5/bin
        
        ./neo4j stop
        
        ./neo4j-admin  dump --database=graph.db --to=/Users/admin/Desktop (保存graph.db.dump文件的地址)
    2. 导入数据库
            
        cd ****/neo4j-community-3.5.5/bin
        
        ./neo4j stop
    
        ./neo4j-admin load --from=****(刚才保存的graph.db.dump文件路径） --database=graph.db --force  

        注：--force 命令会覆盖当前数据库中现有的数据库

./neo4j-admin load --from=/Users/admin/Desktop/SV_NLP_赵亮/KnowledegGraph/生成的neo4j数据库/寻医问药知识图谱graph.db.dump --database=graph.db --force