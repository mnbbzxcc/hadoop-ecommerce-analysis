package com.ecommerce.analysis.config;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

import javax.sql.DataSource;

@Configuration
public class HiveDataSourceConfig {

    @Value("${hive.jdbc.url}")
    private String hiveUrl;

    @Value("${hive.jdbc.driver-class-name}")
    private String driverClassName;

    @Bean(name = "hiveDataSource")
    public DataSource hiveDataSource() {
        DriverManagerDataSource dataSource = new DriverManagerDataSource();
        dataSource.setDriverClassName(driverClassName);
        dataSource.setUrl(hiveUrl);
        // Hive 默认无用户名密码，如有需要可设置
        return dataSource;
    }

    @Bean(name = "hiveJdbcTemplate")
    public JdbcTemplate hiveJdbcTemplate(@Qualifier("hiveDataSource") DataSource dataSource) {
        return new JdbcTemplate(dataSource);
    }
}