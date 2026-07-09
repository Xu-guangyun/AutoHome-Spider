# AutoHome Spider — 汽车之家车型数据采集

采集[汽车之家](https://www.autohome.com.cn/)中型新能源SUV的**车系名称、口碑评分、指导价区间**，并输出多种排序的 CSV 文件。

## 环境配置

### 1. 前置条件

- Python 3.8+
- pip

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install requests pandas
```

依赖包：

| 包名 | 版本（开发环境） | 用途 |
|------|-----------------|------|
| requests | 2.34.2 | HTTP 请求 |
| pandas | 3.0.3 | 数据处理与 CSV 输出 |
| numpy | 2.4.6 | pandas 底层依赖 |

## 使用方法

```bash
python AutoHome_Spider.py
```

运行后脚本会：

1. 逐页抓取车型数据（默认 1–19 页）
2. 解析页面中的 `__NEXT_DATA__` JSON 数据
3. 在控制台打印所有采集结果
4. 在 `autohome_output/` 目录生成 3 个 CSV 文件

## 输出文件

所有 CSV 使用 `utf-8-sig` 编码，可直接用 Excel 打开。

| 文件 | 内容 |
|------|------|
| `autohome_all_data.csv` | 全部采集数据 |
| `autohome_scored_sorted.csv` | 有口碑分的车型，按评分降序排列 |
| `autohome_avg_price_sorted.csv` | 按指导价均值升序排列，含"平均价格(万)"列 |

## 数据字段

| 字段 | 说明 |
|------|------|
| 车系名称 | 车型系列名称 |
| 口碑分 | 用户口碑综合评分 |
| 指导价最低(元) | 官方指导价最低价（元） |
| 指导价最高(元) | 官方指导价最高价（元） |

## 配置说明

- **目标级别**：`BASE_URL` 中的 `levelid_18` 为 SUV 级别，可修改为其他级别 ID
- **翻页范围**：修改 `range(1, 20)` 中的页码范围
- **请求头**：`HEADERS` 中已配置 User-Agent 和 Referer，如遇反爬可自行调整

## 注意事项

- 请合理控制请求频率，避免对目标网站造成压力
- 网站结构可能变更，如解析失败请检查 `__NEXT_DATA__` 字段是否仍然存在
- 采集数据仅供学习参考，请遵守目标网站的 robots.txt 及使用条款
