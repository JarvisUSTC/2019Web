import xlrd
import xlwt
import sys
import math
sys.path.append('../')

class ListNet:

	# self.sumLabel = 0#文件总行数
	# self.feature = []#特征
	# self.weight = []#权重
	# self.label = []#标签
	# self.qid = []#查询id
	# self.doc_ofQid = {}#每个查询的文档数量
	# self.ITER_NUM = 30#迭代次数
	# self.dimention_feature = 11#特征数
	# self.qid_Num = 0#qid数量
	"""docstring for ListNet"""
	def __init__(self):
		super(ListNet, self).__init__()
		self.sumLabel = 0#文件总行数
		self.feature = []#特征
		self.weight = [0.3,0.3,0.3]#[2,2,2,2,2,1,1,1,0.5,0.5,0.5]#权重 
		self.label = []#标签
		self.qid = []#查询id
		self.doc_ofQid = {}#每个查询的文档数量
		self.ITER_NUM = 1000#迭代次数
		self.dimention_feature = 3#特征数 偏置项作为1个特征
		self.qid_Num = 0#qid数量
	
	def ReadExcelFile(self,filepath):
		#读取excel表格数据
		workbook = xlrd.open_workbook(filepath)
		sheet = workbook.sheet_by_name("sheet1")
		self.sumLabel = sheet.nrows - 1
		for i in range(1, sheet.nrows):
			feature_i = sheet.row_values(i)
			feature_temp = []
			for j in range(0, len(feature_i)-1):
				if j == 0:
					feature_temp.append(int(feature_i[j]))
				else:
					feature_temp.append(round(float(feature_i[j]),5))
			#feature_temp.append(1)
			feature_temp.append(int(feature_i[len(feature_i)-1]))
			self.feature.append(feature_temp[1:self.dimention_feature+1])
			self.label.append(feature_temp[self.dimention_feature+1])
			self.qid.append(feature_temp[0])
			if feature_temp[0] not in self.doc_ofQid:
				self.qid_Num = self.qid_Num + 1
				self.doc_ofQid[feature_temp[0]] = 1
			else:
				self.doc_ofQid[feature_temp[0]] = self.doc_ofQid[feature_temp[0]] + 1


	def Learning2Rank(self):
		yita = 0.0003
		print("training...")
		for iterm in range(0, self.ITER_NUM):
			print("---the number of iter:%d"%(iterm))
			now_doc = 0
			for i in range(0, self.qid_Num):
				delta_w = [0]*self.dimention_feature  #delta
				doc_of_i = self.doc_ofQid[i]
				fw = [0]*doc_of_i  #qid对应的每个文档得分
				for k in range(0, doc_of_i):
					for p in range(0,self.dimention_feature):
						fw[p] = fw[p] + self.weight[p]*self.feature[now_doc+k][p]
					#每个文档得分
				#算梯度delta_w
				a = [0]*self.dimention_feature #Sigma p*x
				c = [0]*self.dimention_feature #exp(f(x))*x
				b = 0
				for k in range(doc_of_i):
					temp = [0]*self.dimention_feature
					denominator = 0 #分母
					for m in range(doc_of_i):
						denominator = denominator + math.exp(self.label[now_doc+m])  #我们打上的标签
					p = math.exp(self.label[now_doc+k])/denominator
					for q in range(self.dimention_feature):
						a[q] = a[q] + p*self.feature[now_doc+k][q]
				#a end
				for m in range(doc_of_i):
					b = b + math.exp(fw[m])
				#b end
				for k in range(doc_of_i):
					p = math.exp(fw[k])
					for q in range(self.dimention_feature):
						c[q] = c[q] + p*self.feature[now_doc+k][q]
				for q in range(self.dimention_feature):
					delta_w[q] = (-1)*a[q] + (1.0/b)*c[q]

				for q in range(self.dimention_feature):
					self.weight[q] = self.weight[q] - yita*delta_w[q]

				now_doc = now_doc + doc_of_i
		for i in range(self.dimention_feature):
			print("%d wei: %lf"%(i,self.weight[i]))

	def WriteFileModel(self,file_path):
		self.data_write(file_path,[self.weight])

	def data_write(self,file_path, datas):
		f = xlwt.Workbook()
		sheet1 = f.add_sheet(u'sheet1',cell_overwrite_ok=True) #创建sheet
		
		#将数据写入第 i 行，第 j 列
		i = 0
		for data in datas:
			for j in range(len(data)):
				sheet1.write(i,j,data[j])
			i = i + 1
		
		f.save(file_path) #保存文件	

	def PredictRank(self,file_path):
		scores = []
		scores.append(["qid","score","label"])
		for k in range(self.sumLabel):
			score = 0
			for j in range(self.dimention_feature):
				score = score + self.weight[j]*self.feature[k][j]
			scores.append([self.qid[k],score,self.label[k]])
		self.data_write(file_path,scores)




