import pandas as pd

file_name = "대분류"

df = pd.read_csv(
    f"{file_name}.txt",
    sep=",",            # 구분자가 쉼표가 맞다면 유지, 탭이면 "\t"로 변경
    encoding="utf-8",
    header=None,
    names=["code", "분류"]
)

df.to_csv(f"{file_name}.csv", index=False, encoding="utf-8-sig")
