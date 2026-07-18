package com.ecommerce.analysis.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/offline")
public class OfflineController {

    @Resource(name = "hiveJdbcTemplate")
    private JdbcTemplate hiveJdbcTemplate;

    /**
     * 获取每日统计（PV, UV, 行为分布）
     */
    @GetMapping("/daily-stats")
    public List<Map<String, Object>> getDailyStats() {
        String sql = "SELECT dt, pv, uv, pv_count, buy_count, cart_count, fav_count " +
                "FROM daily_stats ORDER BY dt";
        return hiveJdbcTemplate.queryForList(sql);
    }

    /**
     * 获取指定日期的热门商品 Top N
     * @param date 日期，格式 yyyy-MM-dd
     * @param top 返回前几名，默认10
     */
    @GetMapping("/top-products")
    public List<Map<String, Object>> getTopProducts(
            @RequestParam String date,
            @RequestParam(defaultValue = "10") int top) {
        String sql = "SELECT product_id, pv FROM top_products WHERE dt = '" + date + "' ORDER BY pv DESC LIMIT " + top;
        return hiveJdbcTemplate.queryForList(sql);
    }

    /**
     * 获取指定日期的热门类目 Top N
     */
    @GetMapping("/top-categories")
    public List<Map<String, Object>> getTopCategories(
            @RequestParam String date,
            @RequestParam(defaultValue = "10") int top) {
        String sql = "SELECT category_id, pv FROM top_categories WHERE dt = '" + date + "' ORDER BY pv DESC LIMIT " + top;
        return hiveJdbcTemplate.queryForList(sql);
    }

    /**
     * 获取每小时统计
     * @param date 可选日期，不传则返回所有
     */
    @GetMapping("/hourly-stats")
    public List<Map<String, Object>> getHourlyStats(
            @RequestParam(required = false) String date) {
        String sql = "SELECT dt, hour, pv, uv FROM hourly_stats";
        if (date != null) {
            sql += " WHERE dt = '" + date + "'";
        }
        sql += " ORDER BY dt, hour";
        return hiveJdbcTemplate.queryForList(sql);
    }

    /**
     * 获取转化漏斗数据
     */
    @GetMapping("/funnel")
    public List<Map<String, Object>> getFunnel() {
        String sql = "SELECT dt, pv_uv, cart_uv, buy_uv, pv_to_cart_rate, cart_to_buy_rate " +
                "FROM funnel_stats ORDER BY dt";
        return hiveJdbcTemplate.queryForList(sql);
    }
}