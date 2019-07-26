'''
该文件用来存放之前用过的函数，这些函数都在一些小脚本中使用，在此将其保留下来以便之后在重复使用
'''

def function1(string):
    import re
    '''
    将症状字符串中的[]替换掉，生成两个症状，例如 A[B]C,装换成AC与BC两个
    :param string: 需要替换的字符串 A[B]C 
    :return: 含有所有结果的list
    '''
    string = string.replace('］',']').replace('［','[').replace('（','[').replace('）',']').replace('(','[').replace(')',']')
    a = []
    aa = re.sub(pattern='\s', string=string, repl='')
    start_index = aa.index('[')
    end_index = aa.index(']')
    len = end_index - 1 - start_index
    beixuan1 = aa[:start_index - len] + aa[start_index - len:start_index] + aa[end_index + 1:]
    beixuan2 = aa[:start_index - len] + aa[start_index + 1:end_index] + aa[end_index + 1:]
    if '[' not in beixuan1:
        a.append(beixuan1)
    else:
        a.extend(function1(beixuan1))
    if '[' not in beixuan2:
        a.append(beixuan2)
    else:
        a.extend(function1(beixuan2))
    return a


def function2(string):
    import re
    '''
    将字符串中的()补充字符变成两个，例如 A（B）C，替换成AC 与 ABC 两个
    :param string: 输入的需要转换的字符串 A(B)C
    :return: 含有所有结果的list
    '''
    string = string.replace('（','[').replace('）',']').replace('(','[').replace(')',']')
    a = []
    aa = re.sub(pattern='\s', string=string, repl='')
    start_index = aa.index('[')
    end_index = aa.index(']')
    beixuan1 = aa[:start_index ]  + aa[end_index + 1:]
    beixuan2 = string.replace('[','').replace(']','')
    a.append(beixuan1)
    a.append(beixuan2)
    return a


def jieba_gensim():
    '''
    该函数通过jieba 和 gensim 进行分词得到词向量
    :return:
    '''
    from gensim.models import word2vec
    import jieba
    import pandas as pd
    import re
    f = pd.read_csv('../原始数据/寻医问药网站数据/寻医问药药物数据_enconding_gb18030.csv', encoding='gb18030')
    stopwords = set(open('../原始数据/标准词典/中文停用词表.txt', encoding='utf-8').read().strip('\n').split('\n'))
    jieba.load_userdict('../原始数据/标准词典/全部字典.txt')
    for i in range(f.shape[0]):
    # for i in range(3):
        print(i)
        a = f['药品说明书'].loc[i]
        text = ' '.join(
            [x for x in jieba.lcut(a) if x not in stopwords and len(x) > 1 and x != '\n'])  # 去掉停用词中的词，去掉长度小于等于1的词
        results = re.sub('[（）：:？“”《》，。！·、\d ]+', ' ', text)  # 去标点
        f_write = open('../原始数据/寻医问药网站数据/寻医问药药品说明书.txt', 'a', encoding='utf-8', errors='ignore')
        f_write.write(results)
        f_write.write('\n')

    sentences = word2vec.LineSentence('../原始数据/寻医问药网站数据/寻医问药药品说明书.txt')  # 加载语料,LineSentence用于处理分行分词语料
    model = word2vec.Word2Vec(sentences, size=100, window=5)  # 训练模型就这一句话  去掉出现频率小于2的词
    model.save('寻医问药数据中药品说明书训练的词向量.model')


def FFM(dict,string,max_len):
    '''
    该方法为正向最大匹配，从字典中找到可以匹配出的最长的字符串（葡萄和葡萄糖）
    该方法在 code.get_BIESO_based_rule.get_bieso_byFFM 使用过
    :param dict: 单纯的字典，每个元素都是一个词
    :param string: 输入的字符串，将该字符串中的在字典中的最大匹配的词拿出来
    :param max_len: 正向最大匹配的最大窗口
    :return:
    '''

    result = []
    while string != '':
        word = string[:max_len]
        while 1:
            if word in dict:
                result.append(word)
                break
            else:
                if len(word) == 1:
                    result.append(word)
                    break
                else:
                    word = word[:len(word) - 1]
        string = string[len(word):]
    return result

