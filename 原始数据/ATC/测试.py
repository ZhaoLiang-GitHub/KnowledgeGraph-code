import pandas as pd

f = pd.read_excel('ATC中文药物列表201707.xlsx',sheet_name='Sheet1')
medicine_levle_list = []
level1 = []
level2 = []
level3 = []
level4 = []
level5 = []
for i in range(f.shape[0]):
    ATC_name_CN = f['ATC药物名称（CN）'].loc[i].strip()
    ATC_name_EN = f['ATC药物名称（EN）'].loc[i].strip()
    ATC_label =  f['ATC药物编码'].loc[i]
    name = ATC_name_CN

    if len(ATC_label) == 1:
        level1.append([name,ATC_label])
    elif len(ATC_label) == 3:
        level2.append([name,ATC_label])
    elif len(ATC_label) == 4:
        level3.append([name,ATC_label])
    elif len(ATC_label) == 5:
        level4.append([name,ATC_label])
    elif len(ATC_label) == 7:
        level5.append([name,ATC_label])
print('共有{}个化学式的ATC编码'.format(len(level5)))

for level5_i in level5:
    a = []
    for level1_i in level1:
        if level5_i[1][:1] in level1_i[1]:
            a.append(level1_i[0])
    for level2_i in level2:
        if level5_i[1][:3] in level2_i[1]:
            a.append(level2_i[0])
    for level3_i in level3:
        if level5_i[1][:4] in level3_i[1]:
            a.append(level3_i[0])
    for level4_i in level4:
        if level5_i[1][:5]  in level4_i[1]:
            a.append(level4_i[0])
    a.append(level5_i[0])
    string = '->'.join(a)
    if string !='' :
        medicine_levle_list.append(string)
with open('ATC编码的药品层级结构.txt','w',encoding='utf-8') as f:
    f.write('\n'.join(medicine_levle_list))

