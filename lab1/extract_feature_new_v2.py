import sys
import csv
import xlwt
import numpy as np
import re
maxInt = sys.maxsize
sys.path.append('../')

import jieba
import jieba.analyse

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)


csv_reader = csv.reader(open('查询-文档相关性标签.csv',encoding = 'utf-8'))
information_query = []
f = False
for row in csv_reader:
	if f == True:
		number = row[2]
		newlist = [row[0],row[1],int(number[1:]),int(row[3])]
		information_query.append(newlist)
	else:
		f = True

csv_reader = csv.reader(open('文档数据集.csv',encoding = 'utf-8'))
information_doc = []
f = False
for row in csv_reader:
	if f == True:
		number = row[0]
		newlist = [int(row[0][1:]),row[1],row[2],row[3]]
		information_doc.append(newlist)
	else:
		f = True

for i in range(0, 10):
	print(information_doc[i])
	print(information_query[i])

# hash the doc_id

doc_id = {}
site = 0
for item in information_doc:
	doc_id[item[0]] = site
	site = site + 1
print(information_doc[doc_id[1391166]][3])
def extract(doc,k):
	#jieba.analyse.TFIDF(idf_path="output.txt") 
	tags = jieba.analyse.extract_tags(doc, topK=k, withWeight=1)
	tf_idf = []
	for tag in tags:
		tf_idf.append([tag[0],tag[1]])
	return tf_idf


#query分词之后映射到doc中相应词的tf-idf
# test


def data_write(file_path, datas):
    f = xlwt.Workbook()
    sheet1 = f.add_sheet(u'sheet1',cell_overwrite_ok=True) #创建sheet
    
    #将数据写入第 i 行，第 j 列
    i = 0
    for data in datas:
        for j in range(len(data)):
            sheet1.write(i,j,data[j])
        i = i + 1
        
    f.save(file_path) #保存文件


#
whiteList = {}
count = {}
#白名单
max_score = 0
for query in information_query:
	url = re.split(r'/',information_doc[doc_id[query[2]]][1])
	if url[2] in whiteList:
		whiteList[url[2]] = whiteList[url[2]] + query[3]
		count[url[2]] = count[url[2]]+1;
	else:
		whiteList[url[2]] = query[3]
		count[url[2]] = 1

list_white = []
for i in whiteList:
	whiteList[i] = whiteList[i]/count[i]
	if whiteList[i]>max_score:
		max_score = whiteList[i]
for i in whiteList:
	whiteList[i] = whiteList[i]/max_score
	list_white.append([i,whiteList[i]])
	#归一化
data_write('whiteList.xls', list_white)
#expand
feature_all = []
query_dict = {}
value = 0

for query in information_query:
	if query[0] not in query_dict:
		query_dict[query[0]] = value
		value = value + 1
	seg_list = jieba.analyse.extract_tags(query[0],topK = 100,withWeight = 1)
	title_list = jieba.analyse.extract_tags(query[1],topK = 100,withWeight = 1)
	tags_test = jieba.analyse.extract_tags(information_doc[doc_id[query[2]]][3],topK = 100, withWeight = 1)
	word_tags = {} #doc内容dict
	word_seg = [] #query词
	word_title = {} #标题dict
	tfidf_title = [] #标题tfidf
	tfidf_seg = [] #query tfidf
	tfidf_tags = []
	for item in title_list:
		word_title[item[0]] = item[1]
	for item in seg_list:
		tfidf_seg.append(item[1])
		word_seg.append(item[0])
	for item in tags_test:
		word_tags[item[0]] = item[1]
	feature = []
	feature.append(query_dict[query[0]])
	for item in word_seg:
		if item not in word_tags:
			tfidf_tags.append(0)
		else:
			tfidf_tags.append(word_tags[item])
		if item not in word_title:
			tfidf_title.append(0)
		else:
			tfidf_title.append(word_title[item])
	tfidf_tags = np.mat(tfidf_tags)
	tfidf_seg = np.mat(tfidf_seg)
	tfidf_title = np.mat(tfidf_title)
	num = float(np.dot(tfidf_seg,tfidf_tags.T)) #若为行向量则 A * B.T
	denom = np.linalg.norm(tfidf_seg) * np.linalg.norm(tfidf_tags)
	if denom != 0:
		cos = num / denom #余弦值
		#sim = 0.5 + 0.5 * cos #归一化
		sim = cos
	else:
		sim = 0
	feature.append(sim)
	num = float(np.dot(tfidf_seg,tfidf_title.T)) #若为行向量则 A * B.T
	denom = np.linalg.norm(tfidf_seg) * np.linalg.norm(tfidf_title)
	if denom != 0:
		cos = num / denom #余弦值
		#sim = 0.5 + 0.5 * cos #归一化
		sim = cos
	else:
		sim = 0
	feature.append(sim)
#文档长度作为一个特征
	feature.append(len(information_doc[doc_id[query[2]]][3])/10000)
#url长度
	feature.append(len(information_doc[doc_id[query[2]]][1])/200)
#url质量
	url = re.split(r'/',information_doc[doc_id[query[2]]][1])
	feature.append(whiteList[url[2]])
	feature.append(query[3])
	feature_all.append(feature)
data_write("output_sim.xls", feature_all)



