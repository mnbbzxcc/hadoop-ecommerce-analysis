package com.example.flume.interceptor;

import org.apache.flume.Context;
import org.apache.flume.Event;
import org.apache.flume.interceptor.Interceptor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Map;

public class TimestampExtractor implements Interceptor {

    private static final Logger logger = LoggerFactory.getLogger(TimestampExtractor.class);
    private static final SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");

    @Override
    public void initialize() {}

    @Override
    public Event intercept(Event event) {
        byte[] body = event.getBody();
        String line = new String(body);
        String[] fields = line.split(",");
        if (fields.length >= 5) {
            try {
                // 假设时间戳是第5列（索引4），单位为秒，去除可能的空白
                long timestampSec = Long.parseLong(fields[4].trim());
                Date date = new Date(timestampSec * 1000); // 转换为毫秒
                String dateStr = dateFormat.format(date);
                Map<String, String> headers = event.getHeaders();
                headers.put("timestamp", dateStr);
            } catch (Exception e) {
                logger.error("Failed to parse timestamp from line: {}", line, e);
            }
        } else {
            logger.warn("Invalid line (expected >=5 fields): {}", line);
        }
        return event;
    }

    @Override
    public List<Event> intercept(List<Event> events) {
        for (Event event : events) {
            intercept(event);
        }
        return events;
    }

    @Override
    public void close() {}

    public static class Builder implements Interceptor.Builder {
        @Override
        public Interceptor build() {
            return new TimestampExtractor();
        }

        @Override
        public void configure(Context context) {}
    }
}