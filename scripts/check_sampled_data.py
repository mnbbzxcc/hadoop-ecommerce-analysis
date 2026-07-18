#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检测采样后数据的 UTC 时间分布。
输入文件：UserBehavior_sampled_stratified.csv（无标题行，字段顺序：用户ID,商品ID,商品类目ID,行为类型,时间戳）
输出：控制台打印时间范围、每天每小时的记录数等统计信息。
"""

import csv
import sys
from datetime import datetime, timezone
from collections import defaultdict

def main():
    input_file = "UserBehavior_sampled_stratified.csv"

    min_ts = None
    max_ts = None
    total_records = 0
    hour_counts = defaultdict(int)
    day_counts = defaultdict(int)

    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            for row in reader:
                if len(row) < 5:
                    continue
                try:
                    ts = int(row[4])
                except ValueError:
                    continue

                # 更新最小/最大时间戳
                if min_ts is None or ts < min_ts:
                    min_ts = ts
                if max_ts is None or ts > max_ts:
                    max_ts = ts

                total_records += 1

                hour_start = ts - (ts % 3600)
                hour_counts[hour_start] += 1

                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                day_str = dt.strftime("%Y-%m-%d")
                day_counts[day_str] += 1

        # 空数据检查
        if total_records == 0:
            print("错误：输入文件无有效数据。")
            return

        min_dt = datetime.fromtimestamp(min_ts, tz=timezone.utc)
        max_dt = datetime.fromtimestamp(max_ts, tz=timezone.utc)
        print("=" * 60)
        print(f"文件: {input_file}")
        print(f"总记录数: {total_records:,}")
        print(f"时间范围（UTC）:")
        print(f"  起始: {min_dt.strftime('%Y-%m-%d %H:%M:%S')} (时间戳 {min_ts})")
        print(f"  结束: {max_dt.strftime('%Y-%m-%d %H:%M:%S')} (时间戳 {max_ts})")
        print()

        print("每日记录数统计:")
        for day in sorted(day_counts.keys()):
            print(f"  {day}: {day_counts[day]:,} 条")
        print()

        print("每小时记录数统计（UTC小时）:")
        for hour_start in sorted(hour_counts.keys()):
            dt = datetime.fromtimestamp(hour_start, tz=timezone.utc)
            hour_str = dt.strftime("%Y-%m-%d %H:00")
            print(f"  {hour_str}: {hour_counts[hour_start]:,} 条")
        print("=" * 60)

    # 异常处理
    except FileNotFoundError:
        print(f"错误：找不到输入文件 '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

# 程序入口
if __name__ == "__main__":
    main()