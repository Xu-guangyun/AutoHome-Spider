import os
import requests
import re
import json
import pandas as pd

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.autohome.com.cn/",
}

BASE_URL = "https://www.autohome.com.cn/price/levelid_18/x-x-1-x-{page}"

all_series = []

for page in range(1, 20):
    url = BASE_URL.format(page=page)
    print(f"Fetching page {page}: {url}")

    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.encoding = "utf-8"

    if resp.status_code != 200:
        print(f"  Page {page} returned status {resp.status_code}, stopping.")
        break

    match = re.search(
        r'<script\s+id="__NEXT_DATA__"\s+type="application/json">(.*?)</script>',
        resp.text,
    )
    if not match:
        print(f"  __NEXT_DATA__ not found on page {page}, stopping.")
        break

    data = json.loads(match.group(1))
    page_props = data["props"]["pageProps"]
    series_list = page_props["seriesList"]
    groups = series_list.get("seriesgrouplist", [])

    if not groups:
        print(f"  No series data on page {page}, stopping.")
        break

    for item in groups:
        all_series.append(
            {
                "车系名称": item["seriesname"],
                "口碑分": item.get("average"),
                "指导价最低(元)": item.get("seriesminprice"),
                "指导价最高(元)": item.get("seriesmaxprice"),
            }
        )

    total = series_list.get("seriescount", 0)
    print(f"  Collected {len(groups)} items (total so far: {len(all_series)}/{total})")

print(f"\n总共采集 {len(all_series)} 条数据\n")

# 创建输出文件夹
OUTPUT_DIR = "autohome_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. 输出采集的全部数据
print("=" * 70)
print("1. 采集的全部数据:")
print("=" * 70)
for i, s in enumerate(all_series, 1):
    score = f"{s['口碑分']:.4f}" if s["口碑分"] else "无"
    p_min = s["指导价最低(元)"]
    p_max = s["指导价最高(元)"]
    if p_min and p_max:
        if p_min == p_max:
            price_str = f"{p_min / 10000:.2f}万"
        else:
            price_str = f"{p_min / 10000:.2f}万-{p_max / 10000:.2f}万"
    else:
        price_str = "暂无"
    print(f"  {i:3d}. {s['车系名称']:20s}  口碑分: {score}  指导价: {price_str}")

# 2. 全部数据保存到 CSV
df = pd.DataFrame(all_series)
df["口碑分"] = df["口碑分"].replace(0, pd.NA)
df["指导价最低(元)"] = df["指导价最低(元)"].replace(0, pd.NA)
df["指导价最高(元)"] = df["指导价最高(元)"].replace(0, pd.NA)
csv_all = os.path.join(OUTPUT_DIR, "autohome_all_data.csv")
df_out = df.copy()
df_out["口碑分"] = df_out["口碑分"].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
df_out.to_csv(csv_all, index=False, encoding="utf-8-sig", na_rep="")

# 3. 删除无口碑分数据，按口碑分降序排列，保存到 CSV
df_scored = df.dropna(subset=["口碑分"]).copy()
df_scored = df_scored.sort_values("口碑分", ascending=False)
csv_scored = os.path.join(OUTPUT_DIR, "autohome_scored_sorted.csv")
df_out = df_scored.copy()
df_out["口碑分"] = df_out["口碑分"].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
df_out.to_csv(csv_scored, index=False, encoding="utf-8-sig", na_rep="")

# 4. 计算指导价平均值，按均价升序排列，保存到 CSV
df_price = df.copy()
df_price["平均价格(元)"] = (
    df_price["指导价最低(元)"] + df_price["指导价最高(元)"]
) / 2
df_price_sorted = df_price.sort_values("平均价格(元)")
df_price_sorted["平均价格(万)"] = df_price_sorted["平均价格(元)"] / 10000
csv_price = os.path.join(OUTPUT_DIR, "autohome_avg_price_sorted.csv")
df_out = df_price_sorted.copy()
df_out["口碑分"] = df_out["口碑分"].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
df_out.to_csv(csv_price, index=False, encoding="utf-8-sig", na_rep="", float_format="%.2f")

print(f"\nCSV 文件已保存至 {OUTPUT_DIR}/ 文件夹:")
print(f"  - {csv_all}")
print(f"  - {csv_scored}")
print(f"  - {csv_price}")