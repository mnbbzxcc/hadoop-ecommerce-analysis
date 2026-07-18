-- 外部表，指向HDFS数据
CREATE EXTERNAL TABLE user_behavior (
    user_id INT,
    product_id INT,
    category_id INT,
    behavior STRING,
    ts BIGINT
)
PARTITIONED BY (dt STRING)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 'hdfs://namenode:8020/user/flume/behavior/';