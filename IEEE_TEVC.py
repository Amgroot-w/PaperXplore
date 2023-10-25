import re
import numpy as np
import pandas as pd
from pathlib import Path

def generate_paper_info(info, save_path):
    # 跳过非论文类
    if info['Authors'] is np.nan:
        print('跳过：', info['Document Title'])
        return
    
    # 处理论文题目中的非法字符: *, :, ?, ", >, <, \, /, |
    title_processed = re.sub(r"\\[a-zA-Z]+\s*", "", info['Document Title'])
    title_processed = re.sub(r'[*:?"<>/|]', "_", title_processed)
    
    # 格式化保存文件的路径+名称
    file_name = save_path.joinpath(f"{info['Publication Year']} - {title_processed}.md")

    # 格式化论文题目
    title_formalized = f"[{title_processed}]({info['PDF Link']}) ({info['Publication Year']})"

    # 格式化作者和单位信息
    affiliations_formalized = ''.join([f"*{i+1} - {item}*\n" for i, item in enumerate(info['Author Affiliations'].split("; "))])
    authors_formalized = f"{info['Authors']}\n{affiliations_formalized}"

    # 计算全文页数
    num_pages = int(info['End Page']) - int(info['Start Page']) + 1

    # 构造写入数据
    data = {
        '论文题目': title_formalized,
        '期刊名': info['Publication Title'],
        '作者': authors_formalized,
        '摘要': info['Abstract'],
        '关键字': info['Author Keywords'],
        '页数': num_pages
    }

    # 写入文件
    try:
        with open(file_name, mode='w', encoding='utf8') as f:
            for key, value in data.items():
                f.write(f"**{key}**: {value}\n\n")
    except:
        pass  # debug用


if __name__ == '__main__':
    save_path = Path('results')
    save_path.mkdir(exist_ok=True)

    dirnames = ['meta/IEEE_TEVC_2019_Issue1-6', 
                'meta/IEEE_TEVC_2020_Issue1-6', 
                'meta/IEEE_TEVC_2021_Issue1-6', 
                'meta/IEEE_TEVC_2022_Issue1-6', 
                'meta/IEEE_TEVC_2023_Issue1-5']

    for dirname in dirnames:
        for file_path in Path(dirname).iterdir():
            print('读取：', file_path)

            df = pd.read_csv(file_path)
            for i in range(len(df)):
                generate_paper_info(df.iloc[i, :], save_path)

