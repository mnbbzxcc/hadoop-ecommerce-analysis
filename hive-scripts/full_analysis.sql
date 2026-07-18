-- 增加 MapReduce 任务内存
SET mapreduce.map.memory.mb=2048;
SET mapreduce.reduce.memory.mb=4096;
SET mapreduce.map.java.opts=-Xmx1536m;
SET mapreduce.reduce.java.opts=-Xmx3072m;

-- 开启并行执行（可选）
SET hive.exec.parallel=true;

-- 本地模式下的 JVM 参数（通过 Hive 会话设置）
SET hive.mapred.local.mem=4096;
SET mapreduce.map.memory.mb=4096;
SET mapreduce.reduce.memory.mb=4096;
-- 关闭虚拟内存检查（本地模式可能忽略，但无害）
SET yarn.nodemanager.vmem-check-enabled=false;

-- 启用动态分区
SET hive.exec.dynamic.partition = true;
SET hive.exec.dynamic.partition.mode = nonstrict;

-- 修复所有分区
MSCK REPAIR TABLE user_behavior;

-- 每日统计（覆盖全量）
INSERT OVERWRITE TABLE daily_stats
SELECT 
    dt,
    COUNT(*) AS pv,
    COUNT(DISTINCT user_id) AS uv,
    SUM(CASE WHEN behavior='pv' THEN 1 ELSE 0 END) AS pv_count,
    SUM(CASE WHEN behavior='buy' THEN 1 ELSE 0 END) AS buy_count,
    SUM(CASE WHEN behavior='cart' THEN 1 ELSE 0 END) AS cart_count,
    SUM(CASE WHEN behavior='fav' THEN 1 ELSE 0 END) AS fav_count
FROM user_behavior
GROUP BY dt;

-- 每小时统计（UTC时间）
INSERT OVERWRITE TABLE hourly_stats
SELECT 
    dt,
    HOUR(FROM_UNIXTIME(ts)) AS hour,
    COUNT(*) AS pv,
    COUNT(DISTINCT user_id) AS uv
FROM user_behavior
GROUP BY dt, HOUR(FROM_UNIXTIME(ts));

-- 热门商品 Top 10（按日分区）
INSERT OVERWRITE TABLE top_products PARTITION (dt)
SELECT 
    product_id,
    pv,
    product_rank,
    dt
FROM (
    SELECT 
        dt,
        product_id,
        COUNT(*) AS pv,
        ROW_NUMBER() OVER (PARTITION BY dt ORDER BY COUNT(*) DESC) AS product_rank
    FROM user_behavior
    WHERE behavior='pv'
    GROUP BY dt, product_id
) t
WHERE product_rank <= 10;

-- 热门类目 Top 10（按日分区）
INSERT OVERWRITE TABLE top_categories PARTITION (dt)
SELECT 
    category_id,
    pv,
    category_rank,
    dt
FROM (
    SELECT 
        dt,
        category_id,
        COUNT(*) AS pv,
        ROW_NUMBER() OVER (PARTITION BY dt ORDER BY COUNT(*) DESC) AS category_rank
    FROM user_behavior
    WHERE behavior='pv'
    GROUP BY dt, category_id
) t
WHERE category_rank <= 10;

-- 转化漏斗
INSERT OVERWRITE TABLE funnel_stats
SELECT 
    dt,
    COUNT(DISTINCT CASE WHEN behavior='pv' THEN user_id END) AS pv_uv,
    COUNT(DISTINCT CASE WHEN behavior='cart' THEN user_id END) AS cart_uv,
    COUNT(DISTINCT CASE WHEN behavior='buy' THEN user_id END) AS buy_uv,
    ROUND(COUNT(DISTINCT CASE WHEN behavior='cart' THEN user_id END) * 1.0 / COUNT(DISTINCT CASE WHEN behavior='pv' THEN user_id END), 4) AS pv_to_cart_rate,
    ROUND(COUNT(DISTINCT CASE WHEN behavior='buy' THEN user_id END) * 1.0 / COUNT(DISTINCT CASE WHEN behavior='cart' THEN user_id END), 4) AS cart_to_buy_rate
FROM user_behavior
GROUP BY dt;