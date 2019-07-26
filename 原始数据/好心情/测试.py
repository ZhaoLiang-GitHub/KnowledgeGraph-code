# -*- coding: utf-8 -*-
# @Author: zhaoliang
# @Date:   2019-07-23 17:08:10
# @Email:  zhaoliang1@interns.chuangxin.com
# @Last Modified by:   admin
# @Last Modified time: 2019-07-23 17:34:52
import pandas as pd
import re

def get_announcements():
	# 抽取人工标注的精神病文件中的注意事项

	relation = []
	id_relation = []
	f = pd.read_csv('精神病_注意事项.csv')
	for i in range(f.shape[0]):
		id =f['id'].loc[i]
		announcements = f['注意事项关系'].loc[i]
		if type(announcements) == str:
			# 在人工标注过程中因为表达不一致，需要在后期统一关系的描述
			announcements = announcements.replace('慎重','慎用')
			announcements = announcements.replace('谨慎','慎用')
			announcements = announcements.replace('避免','不宜')
			announcements = announcements.replace('护理','不宜')
			announcements = announcements.replace('禁止','禁忌')
			announcements = announcements.replace('禁用','禁忌')
			announcements = announcements.replace('警告','不宜')
			announcements = announcements.replace('停用','停药')
			announcements = announcements.replace('注意','不宜')
			announcements = announcements.replace('不适用','不宜')
			# 整理之后的注意事项中的关系属性 ['停药',  '减量', '不宜',  '检查', '禁忌', '慎用']
			# 停药：在出现了某种症状或现象后停止吃药
			# 减量：在出现了某种症状或现象后吃药量减少
			# 检查：在吃药后要注意检查某种体征或指标
			# 不宜：某种人（司机，运动员）或者现在得了某种病（感冒发热）不应该吃药，或者说这个要不适用于这些人群，但是并没有说完全不让吃知识需要进一步注意
			# 慎用：某种人或得了某种疾病的人谨慎吃药，慎用比不宜更严重
			# 禁忌：某种人或得了某种疾病的人不能吃药，禁忌比慎用更严重

			announcements = announcements.strip('，').lstrip('-').replace('不宜事项','').replace(',','，')
			announcements_list = announcements.split('，')
			for j in announcements_list :
				entity_relation = j.split('-')
				if len(entity_relation)!=2:
					print('在第{}行的 {} 关系存在错误'.format(i,j))
					print(entity_relation)
				else:
					relation.append(entity_relation[1])
					id_relation.append([id,entity_relation[0],entity_relation[1]])# 得到的每个元素都是【 ID， 实体 ，关系属性 】
		elif type(announcements) == float:
			f['注意事项关系'].loc[i] = ''

	# relation = list(set(relation))
	# print(relation)
	return id_relation


def run():
	# id_relation = get_announcements()
	pass

if __name__ == '__main__':

	run()