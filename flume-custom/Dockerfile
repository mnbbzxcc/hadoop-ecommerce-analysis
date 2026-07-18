FROM probablyfine/flume:2.0.0

# 复制所有 Hadoop JAR 和拦截器 JAR
COPY ./flume-hdfs-lib/*.jar /opt/flume/lib/

# 复制 log4j 配置（可选）
COPY ./flume-conf/log4j.properties /opt/flume-config/log4j.properties