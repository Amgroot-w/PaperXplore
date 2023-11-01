import re
import numpy as np
import pandas as pd
from pathlib import Path

def generate_paper_item(info, save_path):
    """
    生成便于阅读的Markdown文档
        info:  一条文献信息（pd.Series）
        save_path: 结果保存路径（Path对象）
    """

    # 跳过非论文类
    if info['Authors'] is np.nan:
        print('跳过：', info['Document Title'])
        return 0
    
    # 获取发表日期：见刊日期（已正式发表），如果没有则选取在线日期（early access）
    try:
        publish_date = pd.to_datetime(info['Date Added To Xplore']).strftime("%Y-%m-%d")
        online_date = pd.to_datetime(info['Online Date']).strftime("%Y-%m-%d")
        date = publish_date
    except:
        publish_date = 'xxx'
        online_date = pd.to_datetime(info['Online Date']).strftime("%Y-%m-%d")
        date = f"(EarlyAccess){online_date}"

    # 格式化发表时间
    date_formalized = f"{online_date}（在线），{publish_date}（见刊）"

    # 格式化论文题目：处理题目中的非法字符: *, :, ?, ", >, <, \, /, |
    title_formalized = re.sub(r"\\[a-zA-Z]+\s*", "", info['Document Title'])
    title_formalized = re.sub(r'[*:?"<>/|]', "_", title_formalized)

    # 格式化保存文件的路径+名称
    file_name = save_path.joinpath(f"{date} - {title_formalized}.md")

    # 格式化论文题目
    num_pages = int(info['End Page']) - int(info['Start Page']) + 1  # 计算全文页数

    # 格式化作者和单位信息
    affiliations_formalized = ''.join([f"*{i+1} - {item}*\n" for i, item in enumerate(info['Author Affiliations'].split("; "))])
    authors_formalized = f"{info['Authors']}\n{affiliations_formalized}"

    # 格式化关键词
    keywords_splitted = [f"`{item}`" for item in str(info['Author Keywords']).split(";")]
    keywords_formalized = f'; '.join(keywords_splitted)

    # 格式化下载链接
    download_links = f"[期刊官网]({info['PDF Link']}), [SCI-Hub](https://sci-hub.se/{info['DOI']})"

    # 添加阅读进度信息
    progress = "\n\n- [ ] 已完成"

    # 构造写入数据
    data = {
        '论文题目': title_formalized,
        '发表时间': date_formalized,
        '期刊名': info['Publication Title'],
        '作者': authors_formalized,
        '摘要': info['Abstract'],
        '关键词': keywords_formalized,
        '下载链接': download_links,
        '阅读进度': progress,
    }

    # 写入文件
    with open(file_name, mode='w', encoding='utf8') as f:
        for key, value in data.items():
            f.write(f"**{key}**: {value}\n\n")
            
    return 1


if __name__ == '__main__':
    dirnames = [
        'meta/IEEE_TEVC_2019_Issue1-6', 
        'meta/IEEE_TEVC_2020_Issue1-6', 
        'meta/IEEE_TEVC_2021_Issue1-6', 
        'meta/IEEE_TEVC_2022_Issue1-6', 
        'meta/IEEE_TEVC_2023_Issue1-5',
        'meta/IEEE_TEVC_2023_EarlyAccess20231101'
    ]

    save_path = Path('results/TEVC')  # 保存路径
    save_path.mkdir(parents=True, exist_ok=True)

    count = [0, 0]  # 记录文献条目生成数量（跳过数目、成功生成数目）
    for dirname in dirnames:
        for file_path in Path(dirname).iterdir():
            print('读取：', file_path)

            df = pd.read_csv(file_path, index_col=False)
            for i in range(len(df)):
                res = generate_paper_item(df.iloc[i, :], save_path)
                count[res] += 1
                
    print(f'跳过了{count[0]}条非文献信息，成功生成{count[1]}个文献条目！')

