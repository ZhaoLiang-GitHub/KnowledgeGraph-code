'''
从 国家基本药物目录2018版 中抽取出药物的层级结构
因为后期数据经过了人工处理，运行脚本会生成第一版结果
'''

import re

def get_all_medicine():
    with open('./原始数据/化学药品和生物制品索引.txt', 'r', encoding='utf-8') as f:
        # 从索引文件中得到所有的化学药和生物药的名称
        medicine_list = []
        for line in f.readlines():
            stringlist = line.strip('').split(' ')
            for word in stringlist:
                # 当按照空格分开之后，应该得到的药物名称不能为 空、\n、数字（药物页码）、第一二三四画、第一二三四部分、中文笔画索引、-、
                if word != '' and word != '\n' and word != '中文笔画索引' and word != '-' and word != '中文拼音索引' \
                        and not re.match(pattern='[0-9]', string=word) \
                        and not re.match(pattern='[一二三四五六七八九十]*画', string=word) \
                        and not re.match(pattern='第[一二三四]*部分', string=word) \
                        and not re.match(pattern='[一二三四五六七八九十]', string=word) \
                        and not re.match(pattern='[索引]', string=word):

                    # 在按照空格分开之后会出现词中包含了大写英文字母的词，可能是类似"维生素 A"这样的词被切开了，按照规则将其拼接起来，其他的大写字母为索引中的字母不作处理
                    if re.match(pattern='[A-Z].*', string=word):
                        # 类似于"维生素 A"这样的词被分开后，他的特点是 字母前一个词不能是数字(应该是"维生素"这样的中文)也不能是空、字母后一个词不能为空也不能为其他字母
                        if re.match(pattern='[0-9]*', string=stringlist[stringlist.index(word) + 1]) \
                                and stringlist[stringlist.index(word) - 1] != '' \
                                and stringlist[stringlist.index(word) + 1] != '' \
                                and not re.match(pattern='[A-Z]', string=stringlist[stringlist.index(word) - 1]) \
                                and not re.match(pattern='[0-9]', string=stringlist[stringlist.index(word) - 1]):

                            string_beixuan = stringlist[stringlist.index(word) - 1:stringlist.index(word) + 2]
                            # 备选向量中存在 "维生素 A 45(页码)" 和 "维 A 酸 "两种情况
                            if re.match(pattern='[0-9]', string=string_beixuan[-1]):
                                medicine_list.append(''.join(string_beixuan[:-1]))
                            else:
                                medicine_list.append(''.join(string_beixuan))
                        else:
                            pass

                    # 在按照规则分开之后会有 "重组人促红素（CHO 细胞）" 因为含有括号被错误分开的词，按照规则将其拼接起来
                    elif '）' in word and '（' in stringlist[stringlist.index(word) - 1]:
                        string_beixuan = stringlist[stringlist.index(word) - 1:stringlist.index(word) + 1]
                        medicine_list.append(''.join(string_beixuan))
                    elif '（' in word and '）' in stringlist[stringlist.index(word) + 1]:
                        string_beixuan = stringlist[stringlist.index(word):stringlist.index(word) + 2]
                        medicine_list.append(''.join(string_beixuan))

                    # 在按照规则分开后会出现词长度为1的错误词，经查看之后都被处理过了
                    elif len(word) == 1:
                        pass

                    else:
                        medicine_list.append(word)

    with open('./生成文件/化学药品和生物制品_所有药物名称.txt', 'w', encoding='utf-8') as f:
        medicine_list = list(set(medicine_list))
        medicine_list.sort(key=lambda x: len(x))
        f.write('\n'.join(medicine_list))

    return medicine_list

def get_all_levle(medicine_list):
    with open('./原始数据/化学药品和生物制品全文.txt', 'r', encoding='utf-8') as f:
        # 从全文中得到药物的层级关系并写入文件中
        medicine_level = []
        # 得到所有的药物层级结构
        for line in f.readlines():
            # print(line)
            stringlist = line.split(' ')
            for word in stringlist:
                if re.match(pattern='[一二三四五六七八九十]+、', string=word):
                    string_beixuan = stringlist[stringlist.index(word):stringlist.index(word) + 7]
                    a = []
                    for string_beixuan_i in string_beixuan:
                        # if string_beixuan_i == '' or re.match(pattern='\s*',string=string_beixuan_i):
                        if string_beixuan_i == '':
                            a.append(' ')
                        else:
                            a.append(string_beixuan_i)
                    string_beixuan = a[:]
                    string_beixuan_string = ''.join(string_beixuan)
                    # print(string_beixuan_string.split(' ')[0])
                    medicine_level.append(string_beixuan_string.split(' ')[0])
                if re.match(pattern='（[一二三四五六七八九十]+）', string=word):
                    string_beixuan = stringlist[stringlist.index(word):stringlist.index(word) + 7]
                    a = []
                    for string_beixuan_i in string_beixuan:
                        if string_beixuan_i == '':
                            a.append(' ')
                        else:
                            a.append(string_beixuan_i)
                    string_beixuan = a[:]
                    string_beixuan_string = ''.join(string_beixuan)
                    # print(string_beixuan_string.split(' ')[0])
                    medicine_level.append(string_beixuan_string.split(' ')[0])

        f.seek(0)
        all_string = f.read().replace(' ', '').replace('化学药品和生物制品', '')

        # 分级/药物名称 在全文中的位置，根据位置进行分类
        name_index = []
        for medicine_level_i in medicine_level:
            name_index.append([medicine_level_i, all_string.index(medicine_level_i)])

        for medicine_list_i in medicine_list:
            try:
                name_index.append([medicine_list_i, all_string.index(medicine_list_i)])
            except:
                print('错误药物需要人工处理', medicine_list_i)

        name_index.sort(key=lambda x: x[1])

        with open('./生成文件/化学药品和生物制品_层级结构.txt', 'w', encoding='utf-8') as f1:

            for name_index_i in name_index:
                if name_index_i[0] in medicine_level:
                    # print(name_index_i[0])
                    f1.write(name_index_i[0])
                    f1.write('\n')
                elif name_index_i[0] in medicine_list:
                    # print('\t', name_index_i[0])
                    f1.write(''.join(['\t', name_index_i[0]]))
                    f1.write('\n')
        with open('./生成文件/化学药品和生物制品_层级结构_list.txt', 'w', encoding='utf-8') as f2:
            medicine_level_1 = []
            medicine_level_2 = []
            for name_index_i in name_index:
                if name_index_i[0] in medicine_level:
                    if re.match(pattern='[一二三四五六七八九十]*、', string=name_index_i[0]):
                        levle1 = re.sub(pattern='[一二三四五六七八九十]*、', string=name_index_i[0], repl='')
                        medicine_level_1.append(levle1)
                    elif re.match(pattern='（[一二三四五六七八九十]+）', string=name_index_i[0]):
                        levle2 = re.sub(pattern='（[一二三四五六七八九十]+）', string=name_index_i[0], repl='')
                        medicine_level_2.append(levle2)
                elif name_index_i[0] in medicine_list:
                    print(medicine_level_1[-1] + '->' + medicine_level_2[-1] + '->' + name_index_i[0])
                    f2.write(medicine_level_1[-1] + '->' + medicine_level_2[-1] + '->' + name_index_i[0])
                    f2.write('\n')


if __name__ == '__main__':
    # medicine_list = get_all_medicine()
    # get_all_levle(medicine_list)
    pass