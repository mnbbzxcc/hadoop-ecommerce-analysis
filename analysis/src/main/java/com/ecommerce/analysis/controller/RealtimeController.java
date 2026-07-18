package com.ecommerce.analysis.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ZSetOperations;
import org.springframework.web.bind.annotation.*;

import java.util.Set;

@RestController
@RequestMapping("/api/realtime")
public class RealtimeController {

    @Autowired
    private StringRedisTemplate redisTemplate;

    /**
     * 获取累计 PV（从 Flink 写入的 total_pv）
     */
    @GetMapping("/total-pv")
    public String getTotalPV() {
        String pv = redisTemplate.opsForValue().get("realtime:total_pv");
        return pv == null ? "0" : pv;
    }

    /**
     * 获取当前一分钟内的 PV
     * 对应的 Redis key: realtime:minute_pv
     */
    @GetMapping("/pv")
    public String getMinutePV() {
        String pv = redisTemplate.opsForValue().get("realtime:minute_pv");
        return pv == null ? "0" : pv;
    }

    /**
     * 获取当前一分钟内的 UV
     * 对应的 Redis key: realtime:minute_uv
     */
    @GetMapping("/uv")
    public String getMinuteUV() {
        String uv = redisTemplate.opsForValue().get("realtime:minute_uv");
        return uv == null ? "0" : uv;
    }

    /**
     * 获取最近5分钟内的热门商品 Top N
     * 对应的 Redis key: realtime:hot_products_5min (ZSet)
     * @param top 返回前几名，默认10
     */
    @GetMapping("/hot")
    public Set<ZSetOperations.TypedTuple<String>> getHotProducts(
            @RequestParam(defaultValue = "10") int top) {
        return redisTemplate.opsForZSet().reverseRangeWithScores("realtime:hot_products_5min", 0, top - 1);
    }
}