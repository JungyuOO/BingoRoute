"""관광 분류 코드(lclsSystmCode) API를 호출해 CODE CSV를 만든다."""

import os, sys
from datetime import datetime
import pandas as pd

from paths import RAW_DIR

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_system_code(client):
    """대·중·소분류 코드를 순회하며 CSV로 저장한다."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1) 대분류
    system_items = client.get_all_pages("lclsSystmCode2", params={}, num_of_rows=100)
    df_system_code1 = pd.DataFrame(system_items)
    df_system_code1.drop(["rnum"],axis=1,inplace=True)
    df_system_code1["code"] = df_system_code1["code"].astype(str).str.strip().str.lstrip("0")
    df_system_code1["created_at"] = timestamp
    df_system_code1["updated_at"] = timestamp
    df_system_code1.to_csv(RAW_DIR / "system_code1.csv", index=False, encoding="utf-8-sig")
    print(f"[OK] system_code1.csv 저장 ({len(df_system_code1)}건)")

    # 2) 중분류
    system_code_rows = []
    for _, row in df_system_code1.iterrows():
        ac, aname = row["code"], row["name"]
        items = client.get_all_pages("lclsSystmCode2", params={"lclsSystm1": ac}, num_of_rows=100)
        for it in items or []:
            system_code_rows.append({
                "systemCode1": str(ac).lstrip("0"),
                "systemCode2": str(it["code"]).lstrip("0"),
                "systemName2": it["name"],
            })
        print(f"[INFO] 대분류 {ac}({aname}) → 중분류 {len(items or [])}건")

    df_system_code2 = pd.DataFrame(system_code_rows)
    df_system_code2["systemCode1"] = df_system_code2["systemCode1"].astype(str).str.strip().str.lstrip("0")
    df_system_code2["systemCode2"] = df_system_code2["systemCode2"].astype(str).str.strip().str.lstrip("0")
    df_system_code2["created_at"] = timestamp
    df_system_code2["updated_at"] = timestamp
    df_system_code2.to_csv(RAW_DIR / "system_code2.csv", index=False, encoding="utf-8-sig")
    print(f"[OK] system_code2.csv 저장 ({len(df_system_code2)}건)")

    # 3) 소분류
    system_code_rows = []
    for _, arow in df_system_code1.iterrows():
        ac = arow["code"]  # 대분류 코드

        # 이 대분류(ac)에 속한 중분류만 선택
        sub2 = df_system_code2[df_system_code2["systemCode1"] == ac]

        for _, row in sub2.iterrows():
            bc, bname = row["systemCode2"], row["systemName2"]

            # 소분류 조회: 대분류+중분류 모두 전달 (둘 다 필수)
            items = client.get_all_pages(
                "lclsSystmCode2",
                params={"lclsSystm1": ac, "lclsSystm2": bc},
                num_of_rows=100,
            )

            for it in items or []:
                system_code_rows.append({       
                    "systemCode2": str(bc).lstrip("0"),          # 부모(중분류)
                    "systemCode3": str(it["code"]).lstrip("0"),  # 소분류 코드
                    "systemName3": it["name"],  # 소분류 이름
                })

            print(f"[INFO] 중분류 {bc}({bname}) → 소분류 {len(items or [])}건")

    df_system_code3 = pd.DataFrame(system_code_rows)
    df_system_code3["systemCode2"] = df_system_code3["systemCode2"].astype(str).str.strip().str.lstrip("0")
    df_system_code3["systemCode3"] = df_system_code3["systemCode3"].astype(str).str.strip().str.lstrip("0")
    df_system_code3["created_at"] = timestamp
    df_system_code3["updated_at"] = timestamp
    df_system_code3.to_csv(RAW_DIR / "system_code3.csv", index=False, encoding="utf-8-sig")
    print(f"[OK] system_code3.csv 저장 ({len(df_system_code3)}건)")
