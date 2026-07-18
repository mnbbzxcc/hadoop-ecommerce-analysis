#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对清洗后的淘宝用户行为数据进行分层采样，目标采样总数约100万条。
采样策略：
- 时间分层：按 UTC 日期+小时（8天×24小时=192个时间层）
- 保证每个有数据的小时至少采样1条
- 剩余采样名额按各小时原始记录数比例分配
- 最终采样总量接近100万，且保留原始数据的时间分布特征

输入文件：UserBehavior_cleaned.csv（无标题行，字段顺序：用户ID,商品ID,商品类目ID,行为类型,时间戳）
输出文件：UserBehavior_sampled_stratified.csv
"""

import csv
import sys
import random
from collections import defaultdict

def main():
    input_file = "UserBehavior_cleaned.csv"
    output_file = "UserBehavior_sampled_stratified.csv"
    target_total = 1_000_000
    random.seed(42)

    print("=== 第一遍扫描：统计每个小时的数据量 ===")
    hour_counts = defaultdict(int)
    total_records = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            for row in reader:
                if len(row) < 5:
                    continue
                try:
                    ts = int(row[4])
                    hour_start = ts - (ts % 3600)
                except ValueError:
                    continue
                hour_counts[hour_start] += 1
                total_records += 1

                if total_records % 10_000_000 == 0:
                    print(f"  已扫描 {total_records:,} 行")

        print(f"第一遍扫描完成，总记录数: {total_records:,}")
        num_hours = len(hour_counts)
        print(f"有数据的小时数: {num_hours}")

        if total_records == 0:
            print("错误：输入文件无有效数据。")
            return

        remaining = target_total - num_hours
        if remaining < 0:
            print("目标采样数小于有数据的小时数，将只保留每小时1条。")
            remaining = 0

        sample_sizes = {}
        for hour_start, count in hour_counts.items():
            extra = round(remaining * (count / total_records))
            sample_sizes[hour_start] = 1 + extra

        current_total = sum(sample_sizes.values())
        if current_total != target_total:
            diff = target_total - current_total
            hours_list = list(sample_sizes.keys())
            random.shuffle(hours_list)
            for hour_start in hours_list:
                if diff == 0:
                    break
                if sample_sizes[hour_start] < hour_counts[hour_start]:
                    sample_sizes[hour_start] += 1
                    diff -= 1
            if diff != 0:
                print(f"警告：最终采样总数与目标相差 {diff} 条，实际为 {current_total + diff}")

        print("\n各小时采样计划已生成，开始第二遍采样...")

        # 第二遍扫描：蓄水池抽样
        reservoirs = {hour_start: [] for hour_start in sample_sizes}
        counts = {hour_start: 0 for hour_start in sample_sizes}

        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            for row in reader:
                if len(row) < 5:
                    continue
                try:
                    ts = int(row[4])
                    hour_start = ts - (ts % 3600)
                except ValueError:
                    continue

                if hour_start not in sample_sizes:
                    continue

                counts[hour_start] += 1
                target_n = sample_sizes[hour_start]
                reservoir = reservoirs[hour_start]

                if len(reservoir) < target_n:
                    reservoir.append(row)
                else:
                    j = random.randint(0, counts[hour_start] - 1)
                    if j < target_n:
                        reservoir[j] = row

        print("正在写入输出文件...")
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            for hour_start in sorted(sample_sizes.keys()):
                writer.writerows(reservoirs[hour_start])

        sampled_total = sum(len(r) for r in reservoirs.values())
        print(f"\n采样完成！")
        print(f"原始总记录数: {total_records:,}")
        print(f"目标采样总数: {target_total:,}")
        print(f"实际采样总数: {sampled_total:,}")
        print(f"采样比例: {sampled_total / total_records:.4%}")
        print(f"有数据的小时数: {len(sample_sizes)}")
        print(f"输出文件: {output_file}")

    except FileNotFoundError:
        print(f"错误：找不到输入文件 '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()