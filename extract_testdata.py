import sys
import csv
import xlwt
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

def extract(doc,k):
	#jieba.analyse.TFIDF(idf_path="output.txt") 
	tags = jieba.analyse.extract_tags(doc, topK=k, withWeight=1)
	tf_idf = []
	for tag in tags:
		tf_idf.append([tag[0],tag[1]])
	return tf_idf

all_tf_idf = []
output = open('output.txt','w')
for i in range(25):
	doc = information_doc[doc_id[information_query[i][2]]]
	result = extract(doc[3],20)
	for item in result:
		item[1] = round(item[1], 4)
	#result[1] = round(result[1], 4)
	all_tf_idf.append(result)
	#print(result)
print(all_tf_idf,file = output)
output.close()

#query分词之后映射到doc中相应词的tf-idf
# test

query = information_query[0]
seg_list = jieba.cut_for_search(query[0])
tags_test = jieba.analyse.extract_tags(information_doc[doc_id[query[2]]][3],topK = 100, withWeight = 1)
word = {}
for item in tags_test:
	word[item[0]] = item[1]
feature = []
for item in seg_list:
	feature.append(word[item])
print(feature)

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

#expand
feature_all = []
query_dict = {}
value = 0
max_length = 11
for query in information_query:
	if query[0] not in query_dict:
		query_dict[query[0]] = value
		value = value + 1
	seg_list = jieba.cut_for_search(query[0])
	tags_test = jieba.analyse.extract_tags(information_doc[doc_id[query[2]]][3],topK = 100, withWeight = 1)
	word = {}
	for item in tags_test:
		word[item[0]] = item[1]
	feature = []
	feature.append(query_dict[query[0]])
	for item in seg_list:
		if item not in word:
			feature.append(0)
		else:
			feature.append(word[item])
	length = len(feature)
	for i in range(0, max_length + 1 - length):
		feature.append(0)
	feature.append(query[3])
	feature_all.append(feature)
data_write("output.xlsx", feature_all)

