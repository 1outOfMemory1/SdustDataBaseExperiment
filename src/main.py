import sqlparse as sp
import getpass as gp
import json
import entity.Table as Table


username = ""
password = ""

loginInfo = ""
databaseLocation = ".\\databases"
currentDatabase = "abc"
sqlSentences = []


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
    stmts = sp.split(sql)
    for stmt in stmts:
        # 2.format格式化
        print(sp.format(stmt, reindent=True, keyword_case="upper"))
        # 3.解析SQL
        stmt_parsed = sp.parse(stmt)
        print(stmt_parsed[0].tokens)
    return stmt_parsed[0].tokens


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
        print(line)


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


# 只能是 insert delete update select
def myDMLFunction(currentIndex, tokens):
    if not checkCurrentDatabase():
        print("请先选择数据库")
        return
    if afterParseSqlTokens[currentIndex].value.upper() == "INSERT":
        # print("Insert")
        Table.tableInsert(currentDatabase, tokens)
    elif afterParseSqlTokens[currentIndex].value.upper() == "DELETE":
        Table.tableDelete(currentDatabase, tokens)
        # print("DELETE")
    elif afterParseSqlTokens[currentIndex].value.upper() == "UPDATE":
        print("update")
    elif afterParseSqlTokens[currentIndex].value.upper() == "SELECT":
        print("Select")


if __name__ == "__main__":
    # 登录验证 如果用户名和密码错误 无法进入系统
    # while True:
    #     if login():
    #         break
    # 成功通过验证进入系统  进入默认的命令行界面
    while True:
        afterJoinSqlSentence = getASentence()  # 每次获取一个sql语句
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
                    while str(afterParseSqlTokens[index].ttype) != "None":  # 后边一定跟着 要使用的数据库名字
                        index += 1
                        # print(afterParseSqlTokens[index].value)
                    myShowDatabases()
            if str(afterParseSqlTokens[index].ttype) == "Token.Keyword.DML":  # 说明是 SELECT、UPDATE、INSERT、DELETE
                myDMLFunction(index, afterParseSqlTokens)
                break

