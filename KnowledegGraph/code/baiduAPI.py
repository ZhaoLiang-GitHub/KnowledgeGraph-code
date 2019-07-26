import pandas as pd


def baidu_API(text):
    '''
    百度的NLP接口，包括词法句法依存关系等，具体接口在 http://ai.baidu.com/docs#/NLP-Python-SDK/top
    :param string: 输入的句子
    :return:
    '''
    from aip import AipNlp

    # 在百度AI开放平台中下载Python的SDK安装包
    # 创建百度账号后，在百度AI开放平台的控制台中查询,ID 在用户中心，Key和secret在安全中心
    APP_ID = '6b82e45926334c46a8e6b31374d5b43d'  # '你的 App ID'
    API_KEY = 'ba3c712ad3f94ae49327ef2965813b65'  # '你的 Api Key'
    SECRET_KEY = '90f490d485b7418da7d60a5126b51abf'  # '你的 Secret Key'
    client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

    """ 调用依存句法分析 """
    # Query模型：该模型的训练数据来源于用户在百度的日常搜索数据，适用于处理信息需求类的搜索或口语query。
    # Web模型：该模型的训练数据来源于全网网页数据，适用于处理网页文本等书面表达句子。
    options = {}
    options["mode"] = 0 #模型选择。默认值为0，可选值mode=0（对应web模型）；mode=1（对应query模型）
    return client.depParser(text=text,options=options)
    # 词性标注与依存语法的具体标识 http://ai.baidu.com/docs#/NLP-Basic-API/top

if __name__ == '__main__':


    # f_data = pd.read_csv('../寻医问药网站数据/寻医问药药物数据_enconding_gb18030.csv',encoding='GB18030')
    # print(f_data[''])

    # baidu_string = baidu_API('1.妊娠3个月内妇女、有精神病及哺乳期妇女禁用。2.服用单胺氧化酶抑制剂停药不足两周这禁用')
    baidu_string = baidu_API('眼外伤及严重感染时，暂不使用，或遵医嘱')
    print(baidu_string)
    # baidu_string = [{'postag': 'nt', 'head': 2, 'word': '百度', 'id': 1, 'deprel': 'SBV'}, {'postag': 'v', 'head': 0, 'word': '是', 'id': 2, 'deprel': 'HED'}, {'postag': 'm', 'head': 4, 'word': '一', 'id': 3, 'deprel': 'QUN'}, {'postag': 'q', 'head': 6, 'word': '家', 'id': 4, 'deprel': 'ATT'}, {'postag': 'nz', 'head': 6, 'word': '高科技', 'id': 5, 'deprel': 'ATT'}, {'postag': 'n', 'head': 2, 'word': '公司', 'id': 6, 'deprel': 'VOB'}]
    # print(baidu_string)
    baidu_string = baidu_string['items']
    # baidu_string = baidu_string
    arrange = [i['head'] for i in baidu_string ]
    arrange.sort()
    arrange_set = list(set(arrange))
    arrange_set.sort()
    showed = []
    while len(arrange) >0:
        for i in range(len(baidu_string)):
            if baidu_string[i]['head'] == arrange[0]:
                if i not in showed:
                    arrange.pop(0)
                    if baidu_string[i]['head'] - 1 != -1:
                        print(baidu_string[baidu_string[i]['head'] - 1]['word'], end='')
                    else:
                        print('ROOT', end='')
                    print('\t', baidu_string[i]['deprel'], '\t', baidu_string[i]['word'])
                    showed.append(i)
                    break


