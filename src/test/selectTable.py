import pandas as pd
import re
#
#
#
#
# #提取关键词
# def getDataframeByRequirement(key, value, algebraicSymbol, dataframe:pd.DataFrame):
#     print(key)
#     print(value)
#     print(algebraicSymbol)
#     tempDataFrame = None
#     if algebraicSymbol == ">":
#         tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: xx > int(value))]
#     if algebraicSymbol == ">=":
#         tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: xx >= int(value))]
#     if algebraicSymbol == "<":
#         tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: xx < int(value))]
#     if algebraicSymbol == "<=":
#         tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: xx <= int(value))]
#     if algebraicSymbol == "=":
#         tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: str(xx) == str(value))]
#     if algebraicSymbol == "!=":
#         tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: str(xx) != str(value))]
#     return tempDataFrame
#
#
# def getKeyValueAndAlgebraicSymbol(expression: str):
#     key = ""
#     value = ""
#     algebraicSymbol = ""
#     if "=" in expression:
#         equalIndex = expression.index("=")
#         if expression[equalIndex - 1] == "!": algebraicSymbol = "!="
#         elif expression[equalIndex - 1] == ">": algebraicSymbol = ">="
#         elif expression[equalIndex - 1] == "<": algebraicSymbol = "<="
#         else: algebraicSymbol = "="
#     else:
#         if ">" in expression: algebraicSymbol = ">"
#         elif "<" in expression: algebraicSymbol = "<"
#     key = (expression.split(algebraicSymbol))[0].strip()
#     value = (expression.split(algebraicSymbol))[1].strip()
#     tempList = [key, value, algebraicSymbol]
#     return tempList
#
#
# src = "../databases/ABC/student.xlsx"
# writer = pd.ExcelWriter(src)
# attributeDf = pd.read_excel(writer, sheet_name="attribute")
# dataDf = pd.read_excel(writer, sheet_name="data")
# # strTemp3 = "sno< 20 and sno > 5 and sno >=10 and  sno > 17 or sno < 12"
# # strTemp4 = "sno > 17 or sno < 12 "
# noOrDataDf = dataDf
# OrDataDf = dataDf
# sqlStr1 = "SELECT * FROM student"
# sqlStr2 = "SELECT * FROM student where sno< 20 and sno > 5 and sno >=10 and  sno > 17 or sno < 12"
#
#
# p1 = re.search(r'SELECT (.*?) FROM (.*)', sqlStr1)
# print(p1.group(0))
# print(p1.group(1))
# print(p1.group(2))
#
#
# p2 = re.search(r'SELECT (.*?) FROM (.*?) where (.*)', sqlStr2)
# print(p2.group(0))
# print(p2.group(1))
# print(p2.group(2))
# print(p2.group(3))
#
# strTemp3 = p2.group(3)
#
#
# andSplitStrArray = re.split(r" and ", strTemp3)
# orList = []
# for ele in andSplitStrArray:
#     if " or " in ele:
#         orSplitStrArray = re.split(r" or ", ele)
#         orDfList = []
#         oneTempOrDf = pd.DataFrame()
#         # 拿到所有的or 中的表达式 做一个交集
#         for factor in orSplitStrArray:
#             tempArray = getKeyValueAndAlgebraicSymbol(factor)
#             OrDataDf = getDataframeByRequirement(tempArray[0], tempArray[1], tempArray[2], dataDf)
#             orDfList.append(OrDataDf)
#         oneTempOrDf = orDfList[0]
#         # 取所有的并集 用or隔开的表达式的并集
#         for element in orDfList:
#             oneTempOrDf = pd.merge(oneTempOrDf, element, how="outer") # 取并集
#         orList.append(oneTempOrDf)
#     else:
#         tempArray = getKeyValueAndAlgebraicSymbol(ele)
#         key = tempArray[0]
#         value = tempArray[1]
#         algebraicSymbol = tempArray[2]
#         noOrDataDf = getDataframeByRequirement(key, value, algebraicSymbol, noOrDataDf)
# finallyDeleteDf = noOrDataDf
# # 举个例子  sno< 20 and sno > 5 and sno >=10 and  sno > 17 or sno < 12 and  sno > 17 or sno < 12
# # orlist中有 2个元素  最终下方函数是对三个dataframe做交集
# for ele in orList:
#     finallyDeleteDf = pd.merge(finallyDeleteDf, ele, how="inner")
# print(finallyDeleteDf)
#  != = > >= < <=


strTemp = "SELECT * FROM student where sno< 20 and sno > 5 and sno >=10 and  sno > 17 or sno < 12 order   by   sno    asc,name    desc"
strTemp = re.sub(r" +", " ", strTemp)
p3 = re.search(" order by (.*)", strTemp)
print(p3.group(0))
print(p3.group(1))
strTemp = re.sub(r" order by (.*)", "", strTemp)
print(strTemp)

