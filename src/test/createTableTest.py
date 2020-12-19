import re

# file = open("abc.txt")
# tempStr = file.read()
# tempStr = tempStr.replace("\n", "")
tempStr = "     id int  ,     name varchar  ,     age int  ,     school varchar not null,     home varchar not null,     aad varchar,     primary key (id,name),     foreign key (age) references test(age),     foreign key (name) references test(name),     unique key (school,name) "

tempStr =re.search(r"[(](.*)[)]", tempStr).group(1)
print(tempStr + "\n#####################")

print("primary key部分")
p1 = re.search(r"primary key(.*?)[(](.*?)[)]", tempStr)
print(p1.group(0))
print(p1.group(2) + " 主键值")
primaryKey = p1.group(2)
tempStr = re.sub(r"primary key(.*?)[(](.*?)[)]", "", tempStr)

print("#########################\nunique key部分")
p2 = re.search(r"unique key(.*?)[(](.*?)[)]", tempStr)
print(p2.group(0))
print(p2.group(2) + " 唯一键值")
tempStr = re.sub(r"unique key(.*?)[(](.*?)[)]", "", tempStr)


print("#########################\nforeign key部分")
p2 = re.search(r"foreign key(.*?)[(](.*?)[)](.*?)references(.*?)[(](.*?)[)]", tempStr)
print(p2.group(0))
print(p2.group(2) + " 当前表中值")
print(p2.group(4).strip() + " 被参考的表名")
print(p2.group(5).strip() + " 外表的键")
tempStr = re.sub(r"foreign key(.*?)[(](.*?)[)](.*?)references(.*?)[(](.*?)[)]", "", tempStr)

array = tempStr.split(",")
# print(tempStr)
for ele in array:
    print(ele)


# ele = "home               varchar not             null"
# p = re.search(r"(.*?)not( +)null", ele)
# print(p.group(0))
# print(p.group(1))
# print(p.group(2))
# array = re.split(r" +", p.group(1).strip())
# print(array)


# import pandas as pd
# abc = ['id', 'name', 'age', 'school', 'home', 'aad']
# df = pd.DataFrame(columns=abc)
# df.to_excel("abc.xlsx")