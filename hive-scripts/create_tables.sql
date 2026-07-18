-- 每日统计表
CREATE TABLE IF NOT EXISTS daily_stats (
    dt STRING,
    pv BIGINT,
    uv BIGINT,
    pv_count BIGINT,
    buy_count BIGINT,
    cart_count BIGINT,
    fav_count BIGINT
)
STORED AS ORC;

-- 每小时统计表
CREATE TABLE IF NOT EXISTS hourly_stats (
    dt STRING,
    hour INT,
    pv BIGINT,
    uv BIGINT
)
STORED AS ORC;

-- 热门商品表（按日分区）
CREATE TABLE IF NOT EXISTS top_products (
    product_id INT,
    pv BIGINT,
    product_rank INT
)
PARTITIONED BY (dt STRING)
STORED AS ORC;

-- 热门类目表（按日分区）
CREATE TABLE IF NOT EXISTS top_categories (
    category_id INT,
    pv BIGINT,
    category_rank INT
)
PARTITIONED BY (dt STRING)
STORED AS ORC;

-- 转化漏斗表
CREATE TABLE IF NOT EXISTS funnel_stats (
    dt STRING,
    pv_uv INT,
    cart_uv INT,
    buy_uv INT,
    pv_to_cart_rate DOUBLE,
    cart_to_buy_rate DOUBLE
)
STORED AS ORC;