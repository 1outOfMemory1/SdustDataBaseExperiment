import pandas as pd
import re



strTemp1 = "UPDATE my_teacher SET name=lucy"
strTemp2 = "UPDATE my_teacher SET name=lucy where age=30"


# if "where" not in strTemp1:
p1 = re.search(r'UPDATE (.*?) SET (.*?) where (.*)', strTemp2)
print(p1.group(0))  # UPDATE my_teacher SET name=lucy where age=30
print(p1.group(1))  # my_teacher
print(p1.group(2))  # name=lucy
print(p1.group(3))  # age=30
# else:
p2 = re.search(r'UPDATE (.*?) SET (.*)', strTemp1)
print(p2.group(0))  # UPDATE my_teacher SET name=lucy
print(p2.group(1))  # my_teacher
print(p2.group(2))  # name=lucy


