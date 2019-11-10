from ListNet import *

ListNetModel = ListNet()
ListNetModel.ReadExcelFile("output.xls")
ListNetModel.Learning2Rank()
ListNetModel.WriteFileModel("weight.xls")
ListNetModel.PredictRank("scores.xls")