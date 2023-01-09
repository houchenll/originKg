import pandas as pd
from glob import glob
import os
import re

'''
生成论文索引文件：'../resource/paper/paper_index.xls'
    -基于论文标题自动提取：'path', 'title', 'year', 'college'
    -人工标注字段：'stars', 'keywords', 'abstract'

当/resource/paper路径下，新增paper文件时，
    -可以直接运行该文件，将新增paper文件添加进索引文件
    -会基于已有索引文件，自动补充人工标注字段，不会覆盖原信息

'''

# 索引文件保存路径
paper_index_path = '../resource/paper/paper_index.xls'

paper_format = ['caj', 'kdh', 'pdf']


# 递归遍历、保存指定路径下，指定格式的论文
def path_files(path, filelist):
    if os.path.isdir(path):
        for sub_path in glob(f'{path}/*'):
            path_files(sub_path, filelist)
    else:
        if path.split('.')[-1] in paper_format:
            filelist.append(path)


# 基于paper生成paper_index
def create_index():
    filelist = []
    path_files('../resource/paper', filelist)
    df_paper = pd.DataFrame()
    df_paper['title'] = [f.split('/')[-1] for f in filelist]
    df_paper['path'] = filelist
    # 论文标题的唯一性，不能有同名论文
    df_paper = df_paper.drop_duplicates(subset=['title'])

    # 基于此格式提取 year, college：2020_深圳大学_基于知识图谱的电影推荐研究_赵文栋.caj
    df_paper['year'] = df_paper['title'].apply(lambda x: x[:4] if re.search(r'\d', x[:4]) else '')
    df_paper['college'] = df_paper['title'].apply(
        lambda x: re.search(r'_.{4,10}_', x).group()[1:-1] if re.search(r'_.{4,10}_', x) else '')

    # 基于标题，代码自动生成列
    df_paper = df_paper[['title', 'year', 'college', 'path']]

    try:
        # 如果文件已经存在，则提取 'stars', 'keywords', 'abstract'三个人工维护的字段
        df_already = pd.read_excel(paper_index_path)
        # 论文标题的唯一性，不能有同名论文
        df_already = df_already.drop_duplicates(subset=['title'])
        df_already = df_already[['title', 'stars', 'keywords', 'abstract']]
        df_paper = df_paper.merge(df_already, on=['title'])
    except Exception as e:
        print(e)
        df_paper['stars'] = ''
        df_paper['keywords'] = ''
        df_paper['abstract'] = ''

    df_paper = df_paper[['title', 'year', 'college', 'stars', 'keywords', 'abstract', 'path']]
    df_paper.to_excel(paper_index_path, index=False)


if __name__ == '__main__':
    # 生成/resource/paper路径下论文索引；不会覆盖原文件信息
    create_index()
