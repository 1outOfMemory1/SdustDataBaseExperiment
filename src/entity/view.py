import  re

def createView(token):
    tokenStr = ""  # 直接提取出来所有的sql指令  进行正则匹配
    for ele in token:
        tokenStr += ele.normalized
    tokenStr = re.sub(r" +", " ", tokenStr)
    print(tokenStr)
    p1 = re.search(r"CREATE VIEW (.*?) AS (.*)", tokenStr)
    return [p1.group(1), p1.group(0)]

class View:
    viewStr: str = ""