import pandas as pd
import re
strTemp = "DELETE FROM student where home != 'shandong' or id = 30"

p1 = re.search(r'DELETE( +)FROM( +)(.*?)( +)where(.*)', strTemp)
print(p1.group(0))  # DELETE FROM student where home != 'shandong' or id = 30
print(p1.group(3))  # student
print(p1.group(5))  # home != 'shandong' or id = 30
