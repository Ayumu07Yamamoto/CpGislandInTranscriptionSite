# 0. ライブラリのインポート
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 各種データのインポート
# UCSCgenomeBrowserで取得したgeneの座標情報
# UCSCgenomeBrowserで取得したCpGislandの座標情報

file_path = "20250131_gene_refseqcurated"
file_path_cpg = "20250131_CpGisland"
# file_path_cpg_gene = "20250201_CpGislandが転写開始点+-1000にある遺伝子リスト.xlsx"

df_gene = pd.read_csv(file_path, delimiter="\t") # 101,781
df_cpg = pd.read_csv(file_path_cpg, delimiter="\t") # 32,038
# df_cpg_gene = pd.read_excel(file_path_cpg_gene)

# df_geneの加工
# df_geneにはさまざま染色体に含まれる遺伝子情報が含まれている。delete_listにある染色体の行を削除する。
# df_cpgも同様におこなう
delete_list = ['_alt', '_random', '_fix', 'chrUn', 'chrM']
df_gene_i = df_gene[~df_gene['chrom'].str.contains('|'.join(delete_list), na=False)] # delete_list に入っている遺伝子を除く
df_gene_ii = df_gene_i.loc[df_gene_i.groupby('name2')['txStart'].idxmin()] # txStartが最も小さい、エキソンが早く始まるもの

df_cpg_i = df_cpg[~df_cpg['#chrom'].str.contains('|'.join(delete_list), na=False)]

# forループのため2次元リストに変換する
list_gene_ii = df_gene_ii.values.tolist() # ['#name', 'chrom', 'strand', 'txStart', 'txEnd', 'cdsStart', 'cdsEnd', 'exonCount', 'exonStarts', 'exonEnds', 'name2']
list_cpg_i = df_cpg_i.values.tolist() # ['#chrom', 'chromStart', 'chromEnd', 'name', 'length', 'cpgNum', 'gcNum', 'perCpg', 'perGc', 'obsExp']

# 2. cpgislandの初期位置が転写開始地点の+-1000bpの位置にいるものを、遺伝子情報と統合する。
temp_list_i = []
for i in list_cpg_i:
    cpg_chrom = i[0]
    cpg_start = i[1]
    
    temp_list_j = []
    
    for j in list_gene_ii:
        gene_chrom = j[1]
        tx_start = j[3]
        tx_end = j[4]
        gene_name = j[10]

        if gene_chrom == cpg_chrom and cpg_start >= tx_start-1000 and cpg_start <= tx_start+1000:
            append_list = i + j
            temp_list_j.append(append_list)

    if temp_list_j:
        temp_list_i.extend(temp_list_j)

# temp_list_i
temp_df = pd.DataFrame(temp_list_i, columns=['#chrom', 'chromStart', 'chromEnd', 'name', 'length', 'cpgNum', 'gcNum', 'perCpg', 'perGc', 'obsExp', '#name', 'chrom', 'strand', 'txStart', 'txEnd', 'cdsStart', 'cdsEnd', 'exonCount', 'exonStarts', 'exonEnds', 'name2'])
temp_df.to_excel('20250201_CpGislandが転写開始点+-1000にある遺伝子リスト.xlsx', index=False)

# 3. 解析・可視化
  # どれくらいの遺伝子にCpGislandが含まれているか？ -> 29,795の全遺伝子があるうち9,069の遺伝子にCpGが含まれる。他は転写開始地点+-1000bpの領域にCpGが含まれない。
  # CpGislandが含まれている場合、一般にどれくらいの長さのCpGがあるのか？ -> 9,069の遺伝子を対象にヒストグラムで可視化する。
base_feature = ['chromStart','name', 'cpgNum', 'chrom', 'strand', 'txStart', 'txEnd','name2']
gene_base = ['chrom', 'strand', 'txStart', 'txEnd','name2']

df_gene_base = df_gene_ii[gene_base] # 29,795

file_path_cpg_gene = "20250201_CpGislandが転写開始点+-1000にある遺伝子リスト.xlsx"
df_cpg_gene = pd.read_excel(file_path_cpg_gene)
df_cpg_gene_base = df_cpg_gene[base_feature] # 9,376 -> 上記の9,069と異なるのは、ひとつの遺伝子に複数のCpGislandが確認されるため

#df_cpg_gene_base に含まれていない name2 を特定
missing_name2 = set(df_gene_base["name2"]) - set(df_cpg_gene_base["name2"])
#欠損している name2 の DataFrame を作成
df_missing = df_gene_base[df_gene_base["name2"].isin(missing_name2)].copy() # 20,726
df_missing["chromStart"] = np.nan
df_missing["name"] = np.nan
df_missing["cpgNum"] = 0
#不足データを追加
df_cpg_gene_base_extended = pd.concat([df_cpg_gene_base, df_missing], ignore_index=False) # 30,102

# histgram 
sns.histplot(df_cpg_gene_base_extended["cpgNum"], bins=500)
plt.xlim(0, 500)
plt.ylim(0, 500)
# plt.savefig('20250201_一般にどれくらいの長さのCpGがあるのか？.png')
plt.show()

