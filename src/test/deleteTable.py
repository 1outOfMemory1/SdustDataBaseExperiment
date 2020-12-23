import pandas as pd
import re
# strTemp1 = "DELETE           FROM              student           where        home           !=     'shandong'    or    id   =   30"
# strTemp2 = "    DELETE          FROM               student       "

# strTemp1 = re.sub(r" +", " ", strTemp1)
# print(strTemp1)
#
#
# strTemp2 = re.sub(r" +", " ", strTemp2)
# print(strTemp2)

# p1 = re.search(r'DELETE FROM (.*?) where (.*)', strTemp1)
# print(p1.group(0))  # DELETE FROM student where home != 'shandong' or id = 30
# print(p1.group(1))  # student
# print(p1.group(2))  # home != 'shandong' or id = 30


# p2 = re.search(r'DELETE FROM (.*)', strTemp2)
# print(p2.group(0))  # DELETE FROM student
# print(p2.group(1))  # DELETE FROM student

