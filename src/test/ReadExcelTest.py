import pandas as pd
import time
# df = pd.read_excel("../databases/ABC/student.xlsx", sheet_name="data")
# print(df)
# """
# Empty DataFrame
# Columns: [Unnamed: 0, id, name, age, school, home, aad]
# Index: []
# """

# src = "../databases/ABC/student.xlsx"
# writer = pd.ExcelWriter(src)
# dic = {}
# aa = [1, "a", "b", "c", "d"]
# bb = ["id", "name", "school", "home", "aadasf"]
# for index, ele in enumerate(bb):
#     dic[ele] = aa[index]
#
# attributeDf = pd.read_excel(writer, sheet_name="attribute")
# dataDf = pd.read_excel(writer, sheet_name="data", usecols=bb)
#
# pd.set_option('display.max_columns', None)
# attributeDf["value"].at[2] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 更新时间
# attributeDf["value"].at[4] += 1  # 增加行数
# dataDf = dataDf.append(dic, ignore_index=True)
# attributeDf.to_excel(writer, sheet_name="attribute", index=False)
# dataDf.to_excel(writer, sheet_name="data",index=False)
# writer.save()
# writer.close()


#  删除内容
# src = "../databases/ABC/student.xlsx"
# writer = pd.ExcelWriter(src)
# attributeDf = pd.read_excel(writer, sheet_name="attribute")
# dataDf = pd.read_excel(writer, sheet_name="data")
#
# dataDf.drop(dataDf.index, inplace=True)
# attributeDf["value"].at[4] = 0  # 把rowNumber数据行改成0 代表里面没有数据
# attributeDf.to_excel(writer, sheet_name="attribute", index=False)
# dataDf.to_excel(writer, sheet_name="data", index=False)
# writer.save()
# writer.close()
