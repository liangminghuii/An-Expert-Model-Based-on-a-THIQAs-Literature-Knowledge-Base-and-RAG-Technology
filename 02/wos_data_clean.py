# 合并多个文件，可指定某一列
import pandas as pd
import os

# 设置路径
folder_path = r'/kaggle/input/thiq/wos'  # 替换为你的文件夹路径
output_file = r'/kaggle/working/wos.xlsx'  # 输出文件名

# 需要保留的列
required_columns = ['DOI', 'Abstract']

# 创建一个空的DataFrame来存储合并后的数据
combined_data = pd.DataFrame(columns=required_columns)

# 获取文件夹中所有Excel文件
excel_files = [file for file in os.listdir(folder_path)
               if file.endswith(('.xlsx', '.xls', '.xlsm', '.xlsb'))]

if not excel_files:
    print("指定目录中没有找到Excel文件！")
    exit()

# 遍历并合并文件
for file in excel_files:
    file_path = os.path.join(folder_path, file)
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)

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
    combined_data.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\n合并完成！结果已保存到: {os.path.abspath(output_file)}")
    print(f"总合并记录数: {len(combined_data)}")
except Exception as e:
    print(f"保存结果文件时出错: {e}")


def clean_excel_data(input_path, output_path):
    """
    数据清洗专用函数
    参数：
    input_path: 输入文件路径（需包含DOI和Abstract列）
    output_path: 清洗后文件保存路径
    """
    # 读取数据
    df = pd.read_excel(input_path, engine='openpyxl')

    # 验证必要列存在
    required_cols = ['DOI', 'Abstract']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺失必要列: {', '.join(missing_cols)}")

    # 记录原始数据量
    original_count = len(df)

    # 清洗步骤1：删除空值行
    cleaned_df = df.dropna(subset=required_cols, how='any')
    na_removed = original_count - len(cleaned_df)

    # 清洗步骤2：删除完全重复行
    final_df = cleaned_df.drop_duplicates()
    dup_removed = len(cleaned_df) - len(final_df)

    # 生成统计报告
    print(
        f"[数据清洗报告]\n"
        f"---------------------------------\n"
        f"原始数据行数: {original_count}\n"
        f"删除空值行数: {na_removed}\n"
        f"删除重复行数: {dup_removed}\n"
        f"最终有效行数: {len(final_df)}\n"
        f"各列非空统计:"
    )
    # 修正点：移除line_width参数，改用默认格式
    print(final_df.count().to_string())  # 正确写法

    # 保存结果
    final_df.to_excel(output_path, index=False, engine='openpyxl')
    print(f"\n清洗数据已保存至: {output_path}")


# 使用示例
if __name__ == "__main__":
    clean_excel_data(
        input_path="/kaggle/working/THIQs.xlsx",  # 替换为合并后的文件路径
        output_path="/kaggle/working/THIQs_clean.xlsx"  # 清洗结果保存路径
    )