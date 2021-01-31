import  pandas as pd

src = "../databases/ABC/student.xlsx"
df = pd.read_excel(src, sheet_name="data")
print(df)
flag = df.duplicated(subset=["sno", "sname"])
print(flag)