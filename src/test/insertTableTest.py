import re
strTemp = "INSERT INTO student (name, age) value('jack', 30)"

p1 = re.search(r'INSERT( +)INTO( +)(.*?)( +)[(](.*?)[)]( +)value[(](.*?)[)]', strTemp)
print(p1.group(0))  # INSERT INTO student (name, age) value('jack', 30)
print(p1.group(3))  # student
print(p1.group(5))  # name, age
print(p1.group(7))  # 'jack', 30

strTemp = "INSERT INTO student values('lilei',28)"
p2 = re.search(r'INSERT( +)INTO( +)(.*?)( +)values[(](.*?)[)]', strTemp)
print(p2.group(0))  # INSERT INTO my_teacher values('lilei',28)
print(p2.group(3))  # student
print(p2.group(5))  # 'lilei',28
