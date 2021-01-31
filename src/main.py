import os
import re

import sqlparse as sp
import pandas as pd
import getpass as gp
import json
import entity.Table as Table
import entity.view as view


username = ""
password = ""

loginInfo = ""
databaseLocation = ".\\databases"
currentDatabase = ""
sqlSentences = []
mapOfView = {}

def printHeader():
    print("yhnSql> ", end="")


def login():
    global username, password
    username = input("请输入用户名登录数据库：")
    # password = gp.getpass()
    password = input("请输入密码:")
    print(password)

    file = open("config/Login.json")
    jsonStr = json.load(file)  # 解析json
    # print(jsonStr)
    for ele in jsonStr["list"]:
        if str(username) == str(ele["username"]) and str(password) == str(ele["password"]):
            print("登录成功 欢迎您 用户" + username)
            return True
    print("登录失败 用户名或者密码错误")
    return False


def getASentence():
    printHeader()  # 打印头部 yhnSql>
    temp = input()
    if temp == "":
        return None
    while temp[-1] != ";":  # 判断是不是输入完毕了 如果输入完毕了 肯定有分号结尾
        sqlSentences.append(temp)
        sqlSentences.append(" ")
        # print("-> ", end="")
        temp = input()
    sqlSentences.append(temp[:len(temp) - 1])  # 如果没有结束输入 那么直接压入数组
    afterJoinSqlSentence = ""  # 最后拼接的语句
    for ele in sqlSentences:
        afterJoinSqlSentence += ele
    sqlSentences.clear()  # 清空拼接数组 否则会影响到下一个
    # print(sp.format(afterJoinSqlSentence, reindent=True, keyword_case="upper"))
    return afterJoinSqlSentence


def getTokens(sql):
    # 解析SQL
    sql_parsed = sp.parse(sql)
    return sql_parsed[0].tokens



def myMkdir(path: str):
    # 引入模块
    import os
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        print('数据库' + os.path.basename(path) + '创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print('数据库 ' + os.path.basename(path) + ' 已存在')
        return False


def myRemoveDir(path:str):
    # 引入模块
    import os
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则提示删除失败
        print('数据库' + os.path.basename(path) + '不存在，删除失败')
        return False
    else:
        # 如果目录存在则直接删除
        os.rmdir(path)
        print('数据库 ' + os.path.basename(path) + '删除成功')
        return True


def mySelectDatabase(databaseName: str):
    global currentDatabase
    if currentDatabase != databaseName:
        currentDatabase = databaseName.upper()
    print(f"当前选择的数据库为 {currentDatabase}")


def myShowDatabases():
    file = open(databaseLocation + "\\" + "databasesDetail.txt")
    print("当前拥有的数据库有：")
    for line in file:
        print(line, end="")
    print("请输入想要查看的数据库")
    database = input()
    for a, b, c in os.walk(databaseLocation + "\\" + database):  # a代表所在根目录;b代表根目录下所有文件夹(以列表形式存在);c代表根目录下所有文件
        for i in c:
            src = databaseLocation + "\\" + database + "\\" + i
            print(i + "\n#############################")
            print(pd.read_excel(src, sheet_name="attribute", index_col="attribute",
                                usecols=["attribute", "value", "备注"]))
            print("#############################")


def myShowtable(tableName:str):
    src = databaseLocation + "\\" + currentDatabase + "\\" +  tableName + ".xlsx"
    print(pd.read_excel(src, sheet_name="attribute", index_col="attribute",
                        usecols=["attribute", "value", "备注"]))


def myShowIndex (indexName:str):
    src = "./index" + "\\" + currentDatabase + "\\" + indexName
    file = open(src).read()
    print(file)


def myShowView (viewName:str):
    src = "./view" + "\\" + currentDatabase + "\\" + viewName
    file = open(src).read()
    print(file)


def myShowFunction(tokens):
    # print(tokens)
    tokenStr = ""  # 直接提取出来所有的sql指令  进行正则匹配
    for ele in tokens:
        tokenStr += ele.normalized
    print(tokenStr)
    tokenStr = re.sub(r" +", " ", tokenStr)
    # show databases;
    # show table student;
    # show index student;
    # show view student;
    p1 = re.search("SHOW (.*?) (.*)", tokenStr)
    keyWord = ""
    abcObject = ""
    if p1 is not None:
        print(p1.group(1))
        print(p1.group(2))
        keyWord = p1.group(1)
        abcObject = p1.group(2)
    else:
        p2 = re.search("SHOW (.*)", tokenStr)
        print(p2.group(1))
        keyWord = p2.group(1)
    if keyWord == "databases":
        myShowDatabases()
    elif keyWord == "TABLE":
        myShowtable(tableName=abcObject)
    elif keyWord == "INDEX":
        myShowIndex()
    elif keyWord == "INDEX":
        myShowView()





# 如果当前选中了数据库 那么currentDatabase 肯定不为空 用于创建数据表的时候进行验证
def checkCurrentDatabase():
    return len(currentDatabase) > 0


#  target 可能的值有 database user
def myDDLFunction(currentIndex: int, DDl: str, target: str, tokens):
    if DDl == "CREATE":
        if target.upper() == "DATABASE":
            for index in range(currentIndex, len(tokens)):
                while str(tokens[index].ttype) != "None":
                    index += 1
                name = tokens[index].value
            myMkdir(databaseLocation + "\\" + name.upper())
            file = open(databaseLocation + "\\" + "databasesDetail.txt", mode="a")
            file.write(name.upper() + "\n")
            file.close()
        elif target.upper() == "TABLE":
            if not checkCurrentDatabase():
                print("请先选择数据库")
                return
            else:
                tableName = Table.tableInit(databaseLocation, currentDatabase, currentIndex, tokens)
                if tableName != "":
                    print(f"数据库 {currentDatabase} 中的数据表 {tableName} 创建成功")
        elif target.upper() == "USER":
            print("USER")
        elif target.upper() == "VIEW":
            print("VIEW")
            tempList = view.createView(tokens)
            mapOfView[tempList[0]] = tempList[1]
            print(mapOfView)

def checkAuthority(user: str, operation: str):
    print("checkAuthority")
    pass


# 只能是 insert delete update select
def myDMLFunction(currentIndex, tokens):
    if not checkCurrentDatabase():
        print("请先选择数据库")
        return
    #  operation 只能是 insert delete update select
    operation = afterParseSqlTokens[currentIndex].value.upper()
    # checkAuthority()

    if operation == "INSERT":
        # print("Insert")
        Table.tableInsert(currentDatabase, tokens)
    elif operation == "DELETE":
        Table.tableDelete(currentDatabase, tokens)
        # print("DELETE")
    elif operation == "UPDATE":
        Table.tableUpdate(currentDatabase, tokens)
        # print("update")
    elif operation == "SELECT":
        # print("Select")
        Table.tableSelect(currentDatabase, tokens)


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)  # 显示所有列
    pd.set_option('display.max_columns', None)
    # 登录验证 如果用户名和密码错误 无法进入系统
    while True:
        if login():
            break
    # 成功通过验证进入系统  进入默认的命令行界面
    while True:
        afterJoinSqlSentence = getASentence()  # 每次获取一个sql语句
        if afterJoinSqlSentence is None:  # 判断一下什么也不输入的情况 否则会报错
            continue
        # print(afterJoinSqlSentence)
        afterParseSqlTokens = getTokens(afterJoinSqlSentence)
        tempDDL = ""
        tempObject = ""
        tempName = ""
        for index in range(len(afterParseSqlTokens)):
            if str(afterParseSqlTokens[index].ttype) == "Token.Keyword.DDL":  # 说明是 create alter 或者是 drop
                tempDDL = afterParseSqlTokens[index].value.upper()
                index += 1
                while str(afterParseSqlTokens[index].ttype) != "Token.Keyword":
                    index += 1  # 向后查找 关键字  create 后边一定跟随着要操作的对象
                # print(afterParseSqlTokens[index].value) 里边可能是database 、table 、 user 、view 、function、trigger 、procedure
                tempObject = afterParseSqlTokens[index].value  # 临时存储一下子
                myDDLFunction(index, tempDDL, tempObject, afterParseSqlTokens)
            if str(afterParseSqlTokens[index].ttype) == "Token.Keyword":  # 说明是 use
                if afterParseSqlTokens[index].value.upper() == "USE":
                    while str(afterParseSqlTokens[index].ttype) != "None":  # 后边一定跟着 要使用的数据库名字
                        index += 1
                        # print(afterParseSqlTokens[index].value)
                    tempName = afterParseSqlTokens[index].value
                    mySelectDatabase(tempName)
                if afterParseSqlTokens[index].value.upper() == "SHOW":
                    myShowFunction(tokens=afterParseSqlTokens)
            if str(afterParseSqlTokens[index].ttype) == "Token.Keyword.DML":  # 说明是 SELECT、UPDATE、INSERT、DELETE
                myDMLFunction(index, afterParseSqlTokens)
                break

