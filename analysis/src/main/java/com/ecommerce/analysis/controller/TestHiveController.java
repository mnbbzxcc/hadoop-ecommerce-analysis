package com.ecommerce.analysis.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/test")
public class TestHiveController {

    @Resource(name = "hiveJdbcTemplate")
    private JdbcTemplate hiveJdbcTemplate;

    // 测试 daily_stats
    @GetMapping("/daily-stats")
    public List<Map<String, Object>> testDailyStats() {
        String sql = "SELECT * FROM daily_stats ORDER BY dt";
        return hiveJdbcTemplate.queryForList(sql);
    }

    // 测试 hourly_stats
    @GetMapping("/hourly-stats")
    public List<Map<String, Object>> testHourlyStats() {
        String sql = "SELECT * FROM hourly_stats ORDER BY dt, hour";
        return hiveJdbcTemplate.queryForList(sql);
    }

    // 测试 top_products (直接返回所有字段)
    @GetMapping("/top-products")
    public List<Map<String, Object>> testTopProducts(@RequestParam(defaultValue = "10") int limit) {
        String sql = "SELECT * FROM top_products ORDER BY pv DESC LIMIT " + limit;
        return hiveJdbcTemplate.queryForList(sql);
    }

    // 测试 top_categories
    @GetMapping("/top-categories")
    public List<Map<String, Object>> testTopCategories(@RequestParam(defaultValue = "10") int limit) {
        String sql = "SELECT * FROM top_categories ORDER BY pv DESC LIMIT " + limit;
        return hiveJdbcTemplate.queryForList(sql);
    }

    // 测试 funnel_stats
    @GetMapping("/funnel")
    public List<Map<String, Object>> testFunnel() {
        String sql = "SELECT * FROM funnel_stats ORDER BY dt";
        return hiveJdbcTemplate.queryForList(sql);
    }
}