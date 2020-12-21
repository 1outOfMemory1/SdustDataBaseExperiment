# import numpy as np
# import pandas as pd
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

import random
print(random.randrange(1, 10))  # 返回1-10 之间的一个随机数不包括10
print(random.randint(1, 10))  # 返回1-10 之间的一个随机数 包括10
print(random.randrange(0, 10, 2))  # 返回0-10 当中的偶数 2是步长
print(random.random())  # 返回一个0-1之间的随机浮点数
print(random.choice("abcd!@#$%"))  # 返回一个给定数据集合中的随机字符
print(random.sample("abcdefg", 3))  # 返回一个list ['a', 'e', 'c']
