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
        primaryKey = p1.group(2).strip()
        primaryKeyList = primaryKey.split(",")
        for index, ele in enumerate(primaryKeyList):
            primaryKeyList[index] = ele.strip()
        primaryKey = myConcat(primaryKeyList, ",")
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

    uniqueKeyList = uniqueKey.strip().split(",")
    uniqueKey = myConcat(uniqueKeyList, ",")
    # myConcat是自己写的函数  将notNull的column拼接起来  形如 school,home
    notNullColumnStr = myConcat(notNullColumn, ",")
    notNullColumnStr += "," + primaryKey + "," +uniqueKey # 加上主键也不能为空

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
                      owner="root", rowNumber=0, columnNumber=columnCount,
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


def checkSafety(attributeDf, dataDf,  aa: list, dic):
    primaryKeyList: list = attributeDf["value"].at[6].strip().split(",")
    uniqueKeyList: list = attributeDf["value"].at[7].strip().split(",")
    notNullStrArray: list = attributeDf["value"].at[9].strip().split(",")
    error: str = ""
    # 检查 非空约束 primary key
    # print(notNullStrArray)
    for ele in notNullStrArray:
        if ele not in aa:
            # print("字段 " + ele + " 不能为空，插入失败")
            return "字段 " + ele + " 不能为空，插入失败"
    # 主键不能重复
    for ele in primaryKeyList:
        dataDf = dataDf.loc[dataDf[ele].apply(lambda xx: str(xx) == dic[ele])]
    # print(dataDf)
    if dataDf.empty is False:
        # print("主键重复，请重试")
        return "主键重复，请重试"
    return error
    # 唯一键不能重复
    # for ele in uniqueKeyList:
    #     temp = dataDf.loc[dataDf[ele].apply(lambda xx: str(xx) == dic[ele])]


# 这个函数是进行完整性校验无误后 将数据写入到excel表中  tableInsert会调用
def judgeAndInsert(src: str, aa: list, bb: list, all: list):
    # 注意这里的地址 还是相对于main.py 这个文件而言的  而不是相对于 本文件Table.py
    # print(aa)
    # print(bb)
    # aa 是需要插入列表字段列表  bb是值
    writer = pd.ExcelWriter(src)
    dic = {}
    for index, ele in enumerate(bb):
        dic[aa[index]] = ele
    attributeDf = pd.read_excel(writer, sheet_name="attribute")
    #  print(attributeDf)
    dataDf = pd.read_excel(writer, sheet_name="data", usecols=all)
    #  print(dataDf)

    error = checkSafety(attributeDf, dataDf, aa, dic)
    if error != "":
        print(error)
        return

    dataDf = dataDf.append(dic, ignore_index=True)
    attributeDf["value"].at[2] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 更新时间
    attributeDf["value"].at[4] += 1  # 增加行数
    attributeDf.to_excel(writer, sheet_name="attribute", index=False)
    dataDf.to_excel(writer, sheet_name="data", index=False)
    writer.save()
    writer.close()
    print("插入成功")


# 提取关键词 比如  id > 20  key是 id  algebraicSymbol 是 > 20是 value
def getDataframeByRequirement(key, value, algebraicSymbol, dataframe: pd.DataFrame):
    #print(key)
    #print(value)
    #print(algebraicSymbol)
    tempDataFrame = None
    if algebraicSymbol == ">":
        tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: xx > int(value))]
    if algebraicSymbol == ">=":
        tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: xx >= int(value))]
    if algebraicSymbol == "<":
        tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: xx < int(value))]
    if algebraicSymbol == "<=":
        tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: xx <= int(value))]
    if algebraicSymbol == "=":
        tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: str(xx) == str(value))]
    if algebraicSymbol == "!=":
        tempDataFrame = dataframe.loc[dataframe[key].apply(lambda xx: str(xx) != str(value))]
    return tempDataFrame


# 根据表达式 得到一个字符串数组 里边有 tempList = [key, value, algebraicSymbol]
def getKeyValueAndAlgebraicSymbol(expression: str):
    key = ""
    value = ""
    algebraicSymbol = ""
    if "=" in expression:
        equalIndex = expression.index("=")
        if expression[equalIndex - 1] == "!":
            algebraicSymbol = "!="
        elif expression[equalIndex - 1] == ">":
            algebraicSymbol = ">="
        elif expression[equalIndex - 1] == "<":
            algebraicSymbol = "<="
        else:
            algebraicSymbol = "="
    else:
        if ">" in expression:
            algebraicSymbol = ">"
        elif "<" in expression:
            algebraicSymbol = "<"
    key = (expression.split(algebraicSymbol))[0].strip()
    value = (expression.split(algebraicSymbol))[1].strip()
    tempList = [key, value, algebraicSymbol]
    return tempList


# 根据where条件 拿到dataframe数据
def parseWhereGetDf(src: str, whereStr: str):
    dataDf = pd.read_excel(src, sheet_name="data")
    # strTemp3 = "sno< 20 and sno > 5 and sno >=10 and  sno > 17 or sno < 12"
    # strTemp4 = "sno > 17 or sno < 12 "
    noOrDataDf = dataDf

    if whereStr == "":
        # print(dataDf)
        return dataDf
    else:
        andSplitStrArray = re.split(r" and ", whereStr)
        orList = []
        for ele in andSplitStrArray:
            if " or " in ele:
                orSplitStrArray = re.split(r" or ", ele)
                orDfList = []
                # 拿到所有的or 中的表达式 做一个交集
                for factor in orSplitStrArray:
                    tempArray = getKeyValueAndAlgebraicSymbol(factor)
                    OrDataDf = getDataframeByRequirement(tempArray[0], tempArray[1], tempArray[2], dataDf)
                    orDfList.append(OrDataDf)
                oneTempOrDf = orDfList[0]
                # 取所有的并集 用or隔开的表达式的并集
                for element in orDfList:
                    oneTempOrDf = pd.merge(oneTempOrDf, element, how="outer")  # 取并集
                orList.append(oneTempOrDf)
            else:
                tempArray = getKeyValueAndAlgebraicSymbol(ele)
                key = tempArray[0]
                value = tempArray[1]
                algebraicSymbol = tempArray[2]
                noOrDataDf = getDataframeByRequirement(key, value, algebraicSymbol, noOrDataDf)
        finallyDf = noOrDataDf
        # 举个例子  sno< 20 and sno > 5 and sno >=10 and  sno > 17 or sno < 12 and  sno > 17 or sno < 12
        # orlist中有 2个元素  最终下方函数是对三个dataframe做交集
        for ele in orList:
            finallyDf = pd.merge(finallyDf, ele, how="inner")
        # print(finallyDeleteDf)
        return finallyDf


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
    judgeAndInsert(src, columnNameArray, valueArray, allArray)


def handleDeleteInExcel(src: str, whereStr: str):
    # print(src)
    # print(whereStr)
    # 读取数据
    writer = pd.ExcelWriter(src)
    attributeDf = pd.read_excel(writer, sheet_name="attribute")
    dataDf = pd.read_excel(writer, sheet_name="data")
    # print(attributeDf)
    # print(dataDf)

    if whereStr == "":
        # 修改数据
        dataDf.drop(dataDf.index, inplace=True)  # 删除所有数据
        attributeDf["value"].at[4] = 0  # 把rowNumber数据行改成0 代表里面没有数据
    else:
        # print(whereStr)
        # 提取出关键信息 进行筛选
        tempDf = parseWhereGetDf(src=src, whereStr=whereStr)
        # print(dataDf)
        print("删除了{}行".format(len(tempDf)))
        # print(tempDf)
        dataDf = dataDf.append(tempDf)
        dataDf = dataDf.drop_duplicates(subset=dataDf.columns, keep=False)
        # print(dataDf)
        attributeDf["value"].at[4] -= len(tempDf)  # 减少行数

    # 写回数据
    attributeDf.to_excel(writer, sheet_name="attribute", index=False)
    dataDf.to_excel(writer, sheet_name="data", index=False)
    writer.save()
    writer.close()
    print("删除成功")


def tableDelete(currentDatabase: str, token):
    tokenStr = ""  # 直接提取出来所有的sql指令  进行正则匹配
    for ele in token:
        tokenStr += ele.normalized
    # print(tokenStr)

    # 去除多余的空格
    tokenStr = re.sub(r" +", " ", tokenStr)
    tableName: str = ""
    src: str = ""
    whereStr: str = ""
    # 两个分支 如果存在
    if "where" in tokenStr:
        p1 = re.search(r'DELETE FROM (.*?) where (.*)', tokenStr)
        # print(p1.group(0))  # 全语句  DELETE FROM student where home != 'shandong' or id = 30
        # print(p1.group(1))  # 表名 student
        # print(p1.group(2))  # 条件 home != 'shandong' or id = 30
        tableName = p1.group(1).strip()
        whereStr = p1.group(2).strip()
    else:
        p2 = re.search(r'DELETE FROM (.*)', tokenStr)
        # print(p2.group(0))  # DELETE FROM student
        # print(p2.group(1))  # student
        tableName = p2.group(1).strip()
        whereStr = ""
        print("你真的想要删除 {} 表中所有数据吗(yes/no)".format(tableName))
        if "n" in input():
            return
    src = "databases/" + currentDatabase.upper() + "/" + tableName + ".xlsx"
    handleDeleteInExcel(src, whereStr)


# 处理orderby字句的   order by id asc, name desc;  返回列表如右侧  [['id', 'name'], [True, False]]
def getListOfOrderBy(orderByStr: str):
    # print(orderByStr)
    orderByKeyList = []
    orderByValueList = []
    tempArray1 = orderByStr.split(",")
    for ele in tempArray1:
        tempArray2 = ele.split()
        orderByKeyList.append(tempArray2[0].strip())
        if "asc" == tempArray2[1].strip():
            orderByValueList.append(True)
        else:
            orderByValueList.append(False)
    return [orderByKeyList, orderByValueList]


def tableSelect(currentDatabase: str, token):
    tokenStr = ""  # 直接提取出来所有的sql指令  进行正则匹配
    for ele in token:
        tokenStr += ele.normalized
    # 去除多余的空格
    tokenStr = re.sub(r" +", " ", tokenStr)
    tableName: str = ""
    src: str = ""
    whereStr: str = ""
    orderByList = None
    columnStr = ""
    columnStrList = []
    # 处理 order by语句
    if "ORDER BY" in tokenStr:
        p3 = re.search("ORDER BY (.*)", tokenStr)
        # print(p3.group(0))
        # print(p3.group(1))
        orderByStr = p3.group(1).strip()
        orderByList = getListOfOrderBy(orderByStr)
        # print(orderByList)
        tokenStr = re.sub(r" ORDER BY (.*)", "", tokenStr)
    # 正则区分出表名
    if "where" not in tokenStr:
        p1 = re.search(r'SELECT (.*?) FROM (.*)', tokenStr)
        # print(p1.group(0))  # SELECT * FROM student
        # print(p1.group(1))  # *
        columnStr = p1.group(1)

        # print(p1.group(2))  # student
        tableName = p1.group(2)
    else:
        p2 = re.search(r'SELECT (.*?) FROM (.*?) where (.*)', tokenStr)
        # print(p2.group(0))  # SELECT * FROM student where sno< 20 and sno > 5 and sno >=10 and  sno > 17 or sno < 12
        # print(p2.group(1))  # *
        columnStr = p2.group(1)
        # print(p2.group(2))  # student
        # print(p2.group(3))  # sno< 20 and sno > 5 and sno >=10 and  sno > 17 or sno < 12
        tableName = p2.group(2)
        whereStr = p2.group(3)
    # 拿到要显示的字段列表
    if columnStr != "*":
        for ele in columnStr.split(","):
            columnStrList.append(ele.strip())
        # print(columnStrList)
    src = "databases/" + currentDatabase.upper() + "/" + tableName + ".xlsx"
    targetDataframe = parseWhereGetDf(src, whereStr)

    if orderByList is not None:
        targetDataframe.sort_values(by=orderByList[0], inplace=True, ascending=orderByList[1])
    print(targetDataframe[columnStrList if columnStr!="*" else targetDataframe.columns])


# name=姓名测试,id=1
def getListOfUpdateSet(updateStr: str):
    # print(updateStr)
    updateKeyList = []
    updateValueList = []
    tempArray1 = updateStr.split(",")
    for ele in tempArray1:
        tempArray2 = ele.split("=")
        updateKeyList.append(tempArray2[0].strip())
        updateValueList.append(tempArray2[1].strip())
    return [updateKeyList, updateValueList]


def handleUpdateInExcel(src: str, whereStr: str, modifyStr: str):
    writer = pd.ExcelWriter(src)
    attributeDf = pd.read_excel(writer, sheet_name="attribute")
    #  先删除然后再插入
    tempDataframe: pd.DataFrame = parseWhereGetDf(src, whereStr)
    # print(tempDataframe)
    handleDeleteInExcel(src, whereStr)  # 需要进行删完再读
    dataDf: pd.DataFrame = pd.read_excel(writer, sheet_name="data")
    updateList = getListOfUpdateSet(modifyStr)
    # print(updateList)  # [['name', 'id'], ['姓名测试', '1']]
    primaryKeyStr: str = attributeDf["value"].at[6].strip()  # 读出主键
    primaryKeyList = primaryKeyStr.strip().split(",")
    for index, ele in enumerate(primaryKeyList):
        primaryKeyList[index] = ele.strip()
    backUpTempDataframe = tempDataframe.copy(deep=True)
    # print(primaryKeyList)  # 主键的列表
    for index, ele in enumerate(updateList[0]):
        tempDataframe[ele] = updateList[1][index]
    dataTempDf = pd.concat([tempDataframe, dataDf], join="outer", ignore_index=True)  # 取并集
    dataTempDf.to_excel("./temp.xlsx", index=False)
    dataTempDf = pd.read_excel("./temp.xlsx")
    flag = dataTempDf[primaryKeyList].duplicated()
    # 判断是否主键是否重复 如果重复 拒绝修改
    if flag.any() == True:
        print("主键重复 更新失败")
        dataDf = dataDf.append(backUpTempDataframe)
    else:
        print("更新成功")
        dataDf = dataTempDf
    dataDf.sort_values(by=primaryKeyList) # 重新排序
    attributeDf.to_excel(writer, sheet_name="attribute", index=False)
    dataDf.to_excel(writer, sheet_name="data", index=False)
    writer.save()
    writer.close()


def tableUpdate(currentDatabase: str, token):
    tokenStr = ""  # 直接提取出来所有的sql指令  进行正则匹配
    for ele in token:
        tokenStr += ele.normalized
    # 去除多余的空格
    tokenStr = re.sub(r" +", " ", tokenStr)
    tableName: str = ""
    src: str = ""
    whereStr: str = ""
    modifyStr = ""
    modifyList: list = []
    if "where" not in tokenStr:
        p2 = re.search(r'UPDATE (.*?) SET (.*)', tokenStr)
        # print(p2.group(0))  # UPDATE my_teacher SET name=lucy
        # print(p2.group(1))  # my_teacher
        tableName = p2.group(1).strip()
        # print(p2.group(2))  # name=lucy
        modifyStr = p2.group(2).strip()
    else:
        p1 = re.search(r'UPDATE (.*?) SET (.*?) where (.*)', tokenStr)
        # print(p1.group(0))  # UPDATE my_teacher SET name=lucy where age=30
        # print(p1.group(1))  # my_teacher
        tableName = p1.group(1).strip()
        # print(p1.group(2))  # name=lucy
        modifyStr = p1.group(2).strip()
        # print(p1.group(3))  # age=30
        whereStr = p1.group(3).strip()
    src = "databases/" + currentDatabase.upper() + "/" + tableName + ".xlsx"
    handleUpdateInExcel(src, whereStr, modifyStr)


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
