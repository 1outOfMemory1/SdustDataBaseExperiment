import time  # 引入time模块
import pandas as pd
import re
import sqlparse

attributeNameArray = ['tableName', 'createTime', 'lastModifyTime', 'owner', 'rowNumber', 'columnNumber',
                      'primaryKey', 'uniqueKey', 'foreignKey', 'notNullColumn', 'indexColumn', 'columnDataType']
remarksList = ['表名', '创建时间', '最后修改时间', '所有者', '数据行数', '字段数', '主键',
               '唯一键', '外键', '不能为空字段', '索引字段', '数据类型']

# 这个函数是自己的拼接函数   str2TableClass 中会调用
def myConcat(array: list, separator: str):
    temp = ""
    for i in range(0, len(array)):
        temp += array[i] + separator
    temp = temp[:-1]
    return temp


# 这个函数用来根据正则解析传入的create table指令 数据分解出来  tableinit 会调用
def str2TableClass(tempStr: str, tableName: str):
    tempStr = re.search(r"[(](.*)[)]", tempStr).group(1)  # 拿到括号里的内容
    primaryKey = ""
    uniqueKey = ""
    foreignKey = ""

    # primary key部分
    p1 = re.search(r"primary key(.*?)[(](.*?)[)]", tempStr)
    # print(p1.group(0))
    # print(p1.group(2) + " 主键值")
    if p1 is not None:
        primaryKey = p1.group(2)
        tempStr = re.sub(r"primary key(.*?)[(](.*?)[)]", "", tempStr)  # 删除primary key 防止影响到后边内容

    # unique key部分
    p2 = re.search(r"unique key(.*?)[(](.*?)[)]", tempStr)
    # print(p2.group(0))
    # print(p2.group(2) + " 唯一键值")
    if p2 is not None:
        uniqueKey = p2.group(2)
        tempStr = re.sub(r"unique key(.*?)[(](.*?)[)]", "", tempStr)

    # foreign key部分 这里其实有bug foreign key 可以有多个 但是我这里 search方法只能找到一个
    p3 = re.search(r"foreign key(.*?)[(](.*?)[)](.*?)references(.*?)[(](.*?)[)]", tempStr)
    # print(p2.group(0))
    # print(p2.group(2) + " 当前表中值")
    # print(p2.group(4).strip() + " 被参考的表名")
    # print(p2.group(5).strip() + " 外表的键")
    if p3 is not None:
        foreignKey = p3.group(2) + "|" + p3.group(4).strip() + "|" + p3.group(5).strip()
        tempStr = re.sub(r"foreign key(.*?)[(](.*?)[)](.*?)references(.*?)[(](.*?)[)]", "", tempStr)

    # 分解 剩下的 这样里边全都是类似 school varchar not null 、  age int 或者是空格 的字符串
    array = tempStr.split(",")
    tempArray = []  # 用于临时记录去除空格的形如 school varchar not null 这样的
    columnCount = 0  # 用来计数有多少个字段 因为存在全是空格的字符串
    for ele in array:
        if not ele.isspace():  # 自带函数 当全是空格的时候 为 true
            columnCount += 1  # 用来计数有多少个字段 因为存在全是空格的字符串
            tempArray.append(ele.strip())  # 去除前后两边的空格
    columnNameArray = []  # 字段名数组
    columnDataTypeArray = []  # 字段类型数组
    notNullColumn = []  # 设置了不空的字段

    for ele in tempArray:
        p = re.search(r"(.*?)not( +)null", ele)
        if p is None:
            arrayAA = re.split(r" +", ele.strip())
        else:
            arrayAA = re.split(r" +", p.group(1).strip())
            notNullColumn.append(arrayAA[0])
        # 将提取出来的 字段名  和 字段类型 添加进去
        columnNameArray.append(arrayAA[0])
        columnDataTypeArray.append(arrayAA[1])

    # myConcat是自己写的函数  将notNull的column拼接起来  形如 school,home
    notNullColumnStr = myConcat(notNullColumn, ",")

    # 拼接成形如 id#int,name#varchar,age#int,school#varchar,home#varchar,aad#varchar 的字符串
    # 前边是 字段名称 后边是字段类型 两者用#分割 不同字段之间用, 分割
    temp = ""
    for i in range(0, len(columnNameArray)):
        temp += columnNameArray[i] + "#" + columnDataTypeArray[i] + ","
    columnDataTypeArrayStr = temp[:-1]

    # 构造一个类 很好用
    print(tempStr)
    tableTemp = Table(tableName=tableName,
                      createTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                      lastModifyTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                      owner="张三", rowNumber=0, columnNumber=columnCount,
                      primaryKey=primaryKey, uniqueKey=uniqueKey, foreignKey=foreignKey,
                      notNullColumn=notNullColumnStr, indexColumn="", columnDataType=columnDataTypeArrayStr)
    #  将一些信息存入类中 后边还会用
    tableTemp.columnNameArray = columnNameArray
    tableTemp.columnDataTypeArray = columnDataTypeArray
    return tableTemp


# 用来进行表的初始化 主要做的就是提取数据 然后把相关信息写入excel表中去
def tableInit(databaseLocation: str, databaseName: str, currentIndex: int, tokens):
    for index in range(currentIndex, len(tokens)):
        while str(tokens[index].ttype) != "None":
            index += 1
        tableName = str(tokens[index].tokens[0])
        tempStr = str(tokens[index])
        break

    # 引入writer 防止覆盖  这样可以向两个工作表(sheet)中写入信息
    src = databaseLocation + "\\" + databaseName.upper() + "\\" + tableName + ".xlsx"
    writer = pd.ExcelWriter(src, engine='openpyxl')

    initTableAttributeObject = str2TableClass(tempStr, tableName)

    tempArray = list(range(1, len(attributeNameArray) + 1))  # 索引列需要
    s1 = pd.Series(tempArray, index=tempArray, name="index")  # 索引列 一共需要12个属性
    s2 = pd.Series(attributeNameArray, index=tempArray, name="attribute")  # 属性名列
    s3 = pd.Series(initTableAttributeObject.toArray(), index=tempArray, name="value")  # 这个是最麻烦的 注意调用了 Table类的toArray方法
    s4 = pd.Series(remarksList, index=tempArray, name="备注")  # 备注列 这个是写死的
    attributeDf = pd.DataFrame({s1.name: s1, s2.name: s2, s3.name: s3, s4.name: s4})  # 插入4列
    attributeDf = attributeDf.set_index("index")  # 设置索引
    dataDf = pd.DataFrame(columns=initTableAttributeObject.columnNameArray)

    # 将内容写回excel表格
    attributeDf.to_excel(writer, sheet_name="attribute")
    dataDf.to_excel(writer, sheet_name="data", index=False)
    writer.save()
    writer.close()
    return tableName  # 返回创建表的名字


# 这个函数是进行完整性校验无误后 将数据写入到excel表中  tableInsert会调用
def judgeAndInsert(src: str, aa: list, bb: list, all:list):
    # 注意这里的地址 还是相对于main.py 这个文件而言的  而不是相对于 本文件Table.py
    # print(aa)
    # print(bb)

    writer = pd.ExcelWriter(src)
    dic = {}
    for index, ele in enumerate(bb):
        dic[aa[index]] =  ele
    attributeDf = pd.read_excel(writer, sheet_name="attribute")
    #  print(attributeDf)
    dataDf = pd.read_excel(writer, sheet_name="data", usecols=all)
    #  print(dataDf)
    pd.set_option('display.max_columns', None)
    dataDf = dataDf.append(dic, ignore_index=True)
    attributeDf["value"].at[2] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 更新时间
    attributeDf["value"].at[4] += 1  # 增加行数
    attributeDf.to_excel(writer, sheet_name="attribute", index=False)
    dataDf.to_excel(writer, sheet_name="data", index=False)
    writer.save()
    writer.close()


# 外界会调用这个全局函数
def tableInsert(currentDatabase, token):
    # print(token)  # INSERT INTO student (name, age) value('jack', 30)
    tokenStr = ""  # 直接提取出来所有的sql指令  进行正则匹配
    for ele in token:
        tokenStr += ele.normalized
    columnNameArray = []  #
    valueArray = []
    allArray = []
    src = ""

    p1 = re.search(r'INSERT( +)INTO( +)(.*?)( +)[(](.*?)[)]( +)value[(](.*?)[)]', tokenStr)
    if p1 is not None:
        # print(p1.group(0))  # INSERT INTO student (name, age) value('jack', 30)
        # print(p1.group(3))  # student
        tableName = p1.group(3)
        src = "databases/" + currentDatabase.upper() + "/" + tableName + ".xlsx"
        # 求出所有属性 会用到
        attributeDf = pd.read_excel(src, sheet_name="attribute")
        array = str(attributeDf["value"].at[11]).split(",")
        for ele in array:
            allArray.append(ele.split("#")[0])
        # print(p1.group(5))  # name, age
        columnNameArray = p1.group(5).strip().split(",")
        for index in range(0, len(columnNameArray)):
            columnNameArray[index] = columnNameArray[index].strip()
        # print(p1.group(7))  # 'jack', 30
        valueArray = p1.group(7).strip().split(",")
        for index in range(0, len(valueArray)):
            valueArray[index] = valueArray[index].strip().strip("'")
        print(valueArray)
        # print("p1")

    p2 = re.search(r'INSERT( +)INTO( +)(.*?)( +)values[(](.*?)[)]', tokenStr)
    if p2 is not None:
        # print(p2.group(0))  # INSERT INTO my_teacher values('lilei',28)
        # print(p2.group(3))  # student
        tableName = p2.group(3)
        src = "databases/" + currentDatabase.upper() + "/" + tableName + ".xlsx"
        attributeDf = pd.read_excel(src, sheet_name="attribute")
        array = str(attributeDf["value"].at[11]).split(",")
        for ele in array:
            allArray.append(ele.split("#")[0])
        columnNameArray = allArray
        valueArray = p2.group(5).strip().split(",")
        for index in range(0, len(valueArray)):
            valueArray[index] = valueArray[index].strip().strip("'")
    # 调用插入函数  传入 表的路径 字段名称数组  值数组  所有字段数组
    judgeAndInsert(src, columnNameArray, valueArray,allArray)


def tableDelete(database: str, token):
    tokenStr = ""  # 直接提取出来所有的sql指令  进行正则匹配
    for ele in token:
        tokenStr += ele.normalized
    print(tokenStr)

    p1 = re.search(r'DELETE( +)FROM( +)(.*?)( +)where(.*)', tokenStr)
    print(p1.group(0))  # DELETE FROM student where home != 'shandong' or id = 30
    print(p1.group(3))  # student
    print(p1.group(5))  # home != 'shandong' or id = 30
    pass



class Table:
    tableName: str = ""
    createTime: time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    lastModifyTime: time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    owner: str = ""
    rowNumber: int = 0
    columnNumber: int = 0
    primaryKey: str = ""
    uniqueKey: str = ""
    foreignKey: str = ""
    notNullColumn: str = ""
    indexColumn: str = ""
    columnDataType: str = ""
    columnDataTypeArray = []
    columnNameArray = []

    def __init__(self, tableName: str, createTime: time,
                 lastModifyTime: time, owner: str,
                 rowNumber: int, columnNumber: int,
                 primaryKey: str, uniqueKey: str,
                 foreignKey: str, notNullColumn: str,
                 indexColumn: str, columnDataType: str):
        self.tableName = tableName
        self.createTime = createTime
        self.lastModifyTime = lastModifyTime
        self.owner = owner
        self.rowNumber = rowNumber
        self.columnNumber = columnNumber
        self.primaryKey = primaryKey
        self.uniqueKey = uniqueKey
        self.foreignKey = foreignKey
        self.notNullColumn = notNullColumn
        self.indexColumn = indexColumn
        self.columnDataType = columnDataType

    def toArray(self):
        tempArray = [self.tableName, self.createTime,
                     self.lastModifyTime, self.owner,
                     self.rowNumber, self.columnNumber,
                     self.primaryKey, self.uniqueKey,
                     self.foreignKey, self.notNullColumn,
                     self.indexColumn, self.columnDataType]
        return tempArray
