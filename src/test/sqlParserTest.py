import sqlparse
sql = "insert into student (name,age) value('jack',30);"
print(sqlparse.format(sql, reindent=True, keyword_case="upper"))