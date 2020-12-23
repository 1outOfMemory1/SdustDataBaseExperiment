# import numpy as np
import pandas as pd
# df = pd.DataFrame([" aa ", "bb "])
# # testArray = np.array()
# # print(type(testArray))
# # testArray.apply(lambda x:x.strip())
# # df.apply()
# # for index in range(0, len(testArray)):
# #     testArray[index] = testArray[index].strip()
# print(df)

# import sys
# for ele in sys.path:
#     print(ele)


# strTemp = "id#int,name#varchar,age#int,school#varchar,home#varchar,aadasf#varchar"
# array = ['jack', '30']
# for ele in array:
#     print(ele)

# abc = "$$$abc$"
# print(abc)
# print(abc.strip("$"))


# abc = "woshiabc"
# if 3>2:
#     abc = "asfd"
# print(abc)
# array = ['jack', 30]
# print(array[1])


df1 = pd.DataFrame([[1,11,111],[2,22,222],[3,33,333]],columns=['id','data','comment'])
df2 = pd.DataFrame([[0,00,000],[1,11,111],[2,22,222],[4,44,444]],columns=['id','data','comment'])
union_result = pd.merge(df1, df2, how='outer')
union_result = pd.merge(df1, union_result, how='outer')
print(union_result)