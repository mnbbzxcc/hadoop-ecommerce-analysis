import random
import time
import sys
import math

LOG_FILE = r'D:/WSL/hadoop-ecommerce-analysis/sampled_data/user_behavior.log'

BEHAVIORS = ['pv', 'buy', 'cart', 'fav']
BEHAVIOR_WEIGHTS = [0.901, 0.018, 0.054, 0.027]

# 热门商品候选池（可自行调整）
CANDIDATE_PRODUCTS = [
    171794, 241542, 5069556, 3107689, 2915228, 1019316, 3402848, 4558688,
    1388031, 250187, 282578, 4491313, 4372137, 2496172, 5103684
]
HOT_PRODUCT_COUNT = 5
HOT_PRODUCT_PROB = 0.5

# 热门类目候选池
CANDIDATE_CATEGORIES = [
    4756105, 171529, 1275696, 570735, 4145813, 982926, 5071267, 4643350,
    4334671, 3645362, 3175526, 2085092, 3433728
]
HOT_CATEGORY_COUNT = 5
HOT_CATEGORY_PROB = 0.5

# 全局热门池（每隔5分钟更新）
current_hot_products = []
current_hot_categories = []

def exponential_lambda(rate=1.0):
    """生成指数分布间隔（泊松过程），平均间隔 1/rate 秒"""
    return random.expovariate(rate)

def get_sleep_interval():
    """返回下一次事件前的等待时间（秒），模拟真实流量"""
    # 获取当前时间（秒数）
    current_second = time.time()
    # 一天内的秒数
    seconds_in_day = current_second % 86400
    # 模拟高峰时段（例如 10:00-22:00 流量大）
    if 36000 <= seconds_in_day <= 79200:  # 10:00 到 22:00
        # 高峰时段平均每秒 1.5 条
        rate = 1.5
    else:
        # 低峰时段平均每秒 0.5 条
        rate = 0.5
    # 生成指数分布间隔
    return exponential_lambda(rate)

def update_hot_pools():
    """定时更新热门商品和类目池（后台线程）"""
    global current_hot_products, current_hot_categories
    while True:
        current_hot_products = random.sample(CANDIDATE_PRODUCTS, HOT_PRODUCT_COUNT)
        current_hot_categories = random.sample(CANDIDATE_CATEGORIES, HOT_CATEGORY_COUNT)
        print(f"热门商品池更新为: {current_hot_products}")
        print(f"热门类目池更新为: {current_hot_categories}")
        # 每5分钟更新一次
        time.sleep(300)

def generate_line():
    behavior = random.choices(BEHAVIORS, weights=BEHAVIOR_WEIGHTS, k=1)[0]
    user_id = random.randint(1, 10000000)

    if random.random() < HOT_PRODUCT_PROB and current_hot_products:
        product_id = random.choice(current_hot_products)
    else:
        product_id = random.randint(1, 10000000)

    if random.random() < HOT_CATEGORY_PROB and current_hot_categories:
        category_id = random.choice(current_hot_categories)
    else:
        category_id = random.randint(1, 10000000)

    timestamp = int(time.time())
    return f"{user_id},{product_id},{category_id},{behavior},{timestamp}\n"

def main():
    # 启动后台线程更新热门池
    import threading
    updater = threading.Thread(target=update_hot_pools, daemon=True)
    updater.start()

    # 等待初始池生成
    time.sleep(1)

    print("Starting to append to log file (realistic traffic). Press Ctrl+C to stop.")
    try:
        while True:
            line = generate_line()
            with open(LOG_FILE, 'a') as f:
                f.write(line)
                f.flush()
            sys.stdout.write(f"Appended: {line.strip()}\n")
            sys.stdout.flush()
            # 根据当前时段动态计算间隔
            interval = get_sleep_interval()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()