import csv
import os
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def parse_taxonomy_files(tax_dir):
    """解析Taxonomy数据库文件"""
    parent_map = {}
    rank_map = {}
    name_to_taxid = {}
    taxid_to_name = {}

    # 解析 names.dmp
    names_path = os.path.join(tax_dir, 'names.dmp')
    with open(names_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split('|')]
            if len(parts) < 4:
                continue
            taxid, name, name_type = parts[0], parts[1], parts[3]
            if name_type == 'scientific name':
                taxid_to_name[taxid] = name
            if name_type in ['scientific name', 'synonym', 'equivalent name']:
                name_lower = name.lower()
                if name_lower not in name_to_taxid or name_type == 'scientific name':
                    name_to_taxid[name_lower] = taxid

    # 解析 nodes.dmp
    nodes_path = os.path.join(tax_dir, 'nodes.dmp')
    with open(nodes_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split('|')]
            if len(parts) < 3:
                continue
            taxid, parent_id, rank = parts[0], parts[1], parts[2]
            parent_map[taxid] = parent_id
            rank_map[taxid] = rank

    return parent_map, rank_map, name_to_taxid, taxid_to_name


def get_taxonomic_ranks(taxid, parent_map, rank_map, taxid_to_name):
    """获取物种的六级分类信息"""
    target_ranks = {
        'kingdom': '',
        'phylum': '',
        'class': '',
        'order': '',
        'family': '',
        'genus': ''
    }

    # 向上回溯谱系
    current_taxid = taxid
    while current_taxid != '1' and current_taxid in parent_map:
        current_rank = rank_map.get(current_taxid, '')
        current_name = taxid_to_name.get(current_taxid, '')

        # 映射到目标分类等级
        if current_rank == 'superkingdom':
            target_ranks['kingdom'] = current_name
        elif current_rank in target_ranks:
            target_ranks[current_rank] = current_name

        current_taxid = parent_map[current_taxid]

    return [
        target_ranks['kingdom'],
        target_ranks['phylum'],
        target_ranks['class'],
        target_ranks['order'],
        target_ranks['family'],
        target_ranks['genus']
    ]


def add_taxonomy_columns_and_stats(input_csv, output_csv, name_to_taxid, parent_map, rank_map, taxid_to_name):
    """添加分类列并统计分类信息"""
    # 初始化统计
    stats = {
        'total_rows': 0,  # CSV总行数
        'non_empty_species': 0,  # 非空物种数
        'matched_species': 0,  # 匹配物种数
        'unmatched_species': 0,  # 未匹配物种数
        'kingdom_count': set(),  # 界的数目（去重）
        'phylum_count': set(),  # 门的数目（去重）
        'class_count': set(),  # 纲的数目（去重）
        'order_count': set(),  # 目的数目（去重）
        'family_count': set(),  # 科的数目（去重）
        'genus_count': set(),  # 属的数目（去重）
        'species_count': set()  # 物种的数目（去重）
    }

    # 创建新CSV文件
    with open(input_csv, 'r', encoding='utf-8') as infile, \
            open(output_csv, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)
        # 确保原文件有species列
        if 'species' not in reader.fieldnames:
            raise ValueError("CSV文件必须包含'species'列")

        # 添加六列分类信息
        fieldnames = reader.fieldnames + [
            'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus'
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            stats['total_rows'] += 1
            species_name = row['species'].strip() if row['species'] else ''

            # 跳过空物种处理，但保留行
            if not species_name:
                # 添加空分类列
                row.update({
                    'Kingdom': '',
                    'Phylum': '',
                    'Class': '',
                    'Order': '',
                    'Family': '',
                    'Genus': ''
                })
                writer.writerow(row)
                continue

            stats['non_empty_species'] += 1
            stats['species_count'].add(species_name)

            # 尝试匹配物种
            taxid = None
            name_lower = species_name.lower()
            if name_lower in name_to_taxid:
                taxid = name_to_taxid[name_lower]

            # 添加分类信息
            if taxid:
                stats['matched_species'] += 1
                ranks = get_taxonomic_ranks(taxid, parent_map, rank_map, taxid_to_name)
                row.update({
                    'Kingdom': ranks[0],
                    'Phylum': ranks[1],
                    'Class': ranks[2],
                    'Order': ranks[3],
                    'Family': ranks[4],
                    'Genus': ranks[5]
                })

                # 添加到去重统计
                if ranks[0]: stats['kingdom_count'].add(ranks[0])
                if ranks[1]: stats['phylum_count'].add(ranks[1])
                if ranks[2]: stats['class_count'].add(ranks[2])
                if ranks[3]: stats['order_count'].add(ranks[3])
                if ranks[4]: stats['family_count'].add(ranks[4])
                if ranks[5]: stats['genus_count'].add(ranks[5])
            else:
                stats['unmatched_species'] += 1
                # 未匹配的留空
                row.update({
                    'Kingdom': '',
                    'Phylum': '',
                    'Class': '',
                    'Order': '',
                    'Family': '',
                    'Genus': ''
                })

            writer.writerow(row)

    # 计算去重后的数目
    stats['kingdom_count'] = len(stats['kingdom_count'])
    stats['phylum_count'] = len(stats['phylum_count'])
    stats['class_count'] = len(stats['class_count'])
    stats['order_count'] = len(stats['order_count'])
    stats['family_count'] = len(stats['family_count'])
    stats['genus_count'] = len(stats['genus_count'])
    stats['species_count'] = len(stats['species_count'])

    return stats


def plot_taxonomic_levels(stats, output_dir='visualization'):
    """绘制分类层次柱形图"""
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 准备数据
    levels = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
    counts = [
        stats['kingdom_count'],
        stats['phylum_count'],
        stats['class_count'],
        stats['order_count'],
        stats['family_count'],
        stats['genus_count'],
        stats['species_count']
    ]

    # 创建DataFrame
    df = pd.DataFrame({'Classification Level': levels, 'Count': counts})

    # 创建柱形图
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(
        x='Classification Level',
        y='Count',
        data=df,
        palette='viridis'
    )

    # 添加数据标签
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(
            f'{int(height)}',
            (p.get_x() + p.get_width() / 2., height),
            ha='center', va='center',
            xytext=(0, 10),
            textcoords='offset points',
            fontsize=10
        )

    plt.title('Taxonomic Diversity Across Classification Levels', fontsize=16)
    plt.xlabel('Classification Level', fontsize=12)
    plt.ylabel('Number of Taxa', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # 保存图表
    plt.savefig(os.path.join(output_dir, 'taxonomic_levels.png'), dpi=300)
    plt.close()

    return df


def main():
    """主函数"""
    # 配置路径
    tax_dir = "/kaggle/input/species-classification/taxonkit"  # Taxonomy文件目录
    input_csv = "/kaggle/input/species-classification/THIQ.csv"  # 输入的原始CSV文件
    output_csv = "classified_THIQ.csv"  # 带分类信息的新CSV
    visualization_dir = "/kaggle/working/taxonomy_visualization"  # 可视化结果目录

    # 1. 解析数据库文件
    print("解析Taxonomy数据库文件...")
    parent_map, rank_map, name_to_taxid, taxid_to_name = parse_taxonomy_files(tax_dir)
    print(f"解析完成！共加载 {len(name_to_taxid)} 个分类名称")

    # 2. 添加分类列并统计
    print("处理CSV文件并添加分类信息...")
    stats = add_taxonomy_columns_and_stats(
        input_csv, output_csv,
        name_to_taxid, parent_map, rank_map, taxid_to_name
    )

    # 3. 输出统计结果
    print("\n=== 分类统计结果 ===")
    print(f"CSV总行数: {stats['total_rows']}")
    print(f"非空物种数: {stats['non_empty_species']}")
    print(f"匹配物种数: {stats['matched_species']}")
    print(f"未匹配物种数: {stats['unmatched_species']}")
    print(f"\n各分类层次的数目:")
    print(f"  界 (Kingdom): {stats['kingdom_count']}")
    print(f"  门 (Phylum): {stats['phylum_count']}")
    print(f"  纲 (Class): {stats['class_count']}")
    print(f"  目 (Order): {stats['order_count']}")
    print(f"  科 (Family): {stats['family_count']}")
    print(f"  属 (Genus): {stats['genus_count']}")
    print(f"  物种 (Species): {stats['species_count']}")

    # 4. 绘制分类层次柱形图
    print("\n创建分类层次柱形图...")
    plot_taxonomic_levels(stats, visualization_dir)
    print(f"图表已保存到: {visualization_dir}/taxonomic_levels.png")

    print(f"\n处理完成！带分类信息的数据已保存到: {output_csv}")


if __name__ == '__main__':
    main()