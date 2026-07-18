package com.ecommerce.analysis.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/test")
public class TestController {

    @Autowired
    private StringRedisTemplate redisTemplate;

    @Resource(name = "hiveJdbcTemplate")
    private JdbcTemplate hiveJdbcTemplate;

    @GetMapping("/redis")
    public String testRedis() {
        redisTemplate.opsForValue().set("test:key", "Hello from SpringBoot!");
        return "Redis set success. Value: " + redisTemplate.opsForValue().get("test:key");
    }

    @GetMapping("/hive")
    public List<Map<String, Object>> testHive() {
        String sql = "SHOW DATABASES";
        return hiveJdbcTemplate.queryForList(sql);
    }
}