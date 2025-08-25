# 合并csv文件（因为scopus数据库导出的是csv文件）
import pandas as pd
import os

# 设置路径
folder_path = r'/kaggle/input/thiq/scopus'  # 替换为你的文件夹路径
output_file = r'/kaggle/working/thiq.csv'  # 输出文件名

# 需要保留的列
required_columns = ['DOI', '摘要']

# 创建一个空的DataFrame来存储合并后的数据
combined_data = pd.DataFrame(columns=required_columns)

# 获取文件夹中所有CSV文件
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

if not csv_files:
    print("指定目录中没有找到CSV文件！")
    exit()

# 遍历并合并文件
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)

        # 检查是否包含所需列
        available_columns = [col for col in required_columns if col in df.columns]

        if not available_columns:
            print(f"文件 {file} 中未找到任何所需列，跳过...")
            continue

        # 只保留需要的列
        df_filtered = df[available_columns]

        # 添加缺失的列（如果有）
        for col in set(required_columns) - set(available_columns):
            df_filtered[col] = None

        # 按要求的列顺序排列
        df_filtered = df_filtered[required_columns]

        # 合并数据
        combined_data = pd.concat([combined_data, df_filtered], ignore_index=True)

        print(f"已处理文件: {file}")

    except Exception as e:
        print(f"处理文件 {file} 时出错: {e}")

# 保存合并后的文件
try:
    combined_data.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n合并完成！结果已保存到: {os.path.abspath(output_file)}")
    print(f"总合并记录数: {len(combined_data)}")
except Exception as e:
    print(f"保存结果文件时出错: {e}")


# scopus数据库csv文件清洗
def clean_data(input_path, output_path):
    """
    数据清洗专用函数
    参数：
    input_path: 输入文件路径（需包含DOI和Abstract列）
    output_path: 清洗后文件保存路径
    """
    # 读取数据
    df = pd.read_csv(input_path)
    df.columns = ['DOI', 'Abstract'] #将原来的列名['DOI', '摘要'] 修改为 ['DOI', 'Abstract']

    # 验证必要列存在
    required_cols = ['DOI', 'Abstract']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺失必要列: {', '.join(missing_cols)}")

    # 记录原始数据量
    original_count = len(df)

    # 清洗步骤1：
    cleaned_df = df.loc[~ (df['DOI'].isna() | (df['摘要'] == "[No abstract available]"))]

    # 计算删除的行数
    removed_count = original_count - len(cleaned_df)

    # 清洗步骤2：删除完全重复行
    final_df = cleaned_df.drop_duplicates()
    dup_removed = len(cleaned_df) - len(final_df)

    # 生成统计报告
    print(
        f"[数据清洗报告]\n"
        f"---------------------------------\n"
        f"原始数据行数: {original_count}\n"
        f"删除空值行数: {removed_count}\n"
        f"删除重复行数: {dup_removed}\n"
        f"最终有效行数: {len(final_df)}\n"
        f"各列非空统计:"
    )
    print(final_df.count().to_string())  # 正确写法

    # 保存结果
    final_df.to_excel(output_path, index=False, engine='openpyxl')
    print(f"\n清洗数据已保存至: {output_path}")


# 使用示例
if __name__ == "__main__":
    clean_data(
        input_path="/kaggle/working/thiq.csv",  # 替换为合并后的CSV文件路径
        output_path="/kaggle/working/thiq.xlsx"  # 清洗结果保存路径
    )