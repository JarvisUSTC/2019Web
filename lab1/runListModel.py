from ListNet_sim import *

ListNetModel = ListNet()
ListNetModel.ReadExcelFile("output_sim.xls")
ListNetModel.Learning2Rank()
ListNetModel.WriteFileModel("weight_sim.xls")
ListNetModel.PredictRank("scores_sim.xls")