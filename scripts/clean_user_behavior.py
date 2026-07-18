#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
清理淘宝用户行为数据集，过滤掉时间戳不在指定日期范围内的记录。
输入文件：UserBehavior.csv（无标题行，逗号分隔，字段顺序：用户ID,商品ID,商品类目ID,行为类型,时间戳）
输出文件：UserBehavior_cleaned.csv
日期范围：2017-11-25 00:00:00 UTC 至 2017-12-02 23:59:59 UTC（包含边界）
"""

import csv
import sys
from datetime import datetime, timezone

def main():
    # 输入/输出文件名
    input_file = "UserBehavior.csv"
    output_file = "UserBehavior_cleaned.csv"

    # 起始和结束日期（UTC）
    start_date = datetime(2017, 11, 25, 0, 0, 0, tzinfo=timezone.utc)
    end_date   = datetime(2017, 12, 2, 23, 59, 59, tzinfo=timezone.utc)

    # Unix时间戳
    start_ts = int(start_date.timestamp())
    end_ts   = int(end_date.timestamp())

    # 计数器初始化
    processed = 0
    kept = 0

    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            for row in reader:
                processed += 1
                if processed % 1_000_000 == 0:
                    print(f"已处理 {processed} 行，保留 {kept} 行")

                if len(row) < 5:
                    continue

                try:
                    ts = int(row[4])
                except ValueError:
                    continue

                if start_ts <= ts <= end_ts:
                    writer.writerow(row)
                    kept += 1

        print(f"\n处理完成！")
        print(f"总处理行数: {processed}")
        print(f"保留行数: {kept}")
        print(f"输出文件: {output_file}")

    # 异常处理
    except FileNotFoundError:
        print(f"错误：找不到输入文件 '{input_file}'，请确认文件路径正确。")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

    # 程序入口
if __name__ == "__main__":
    main()