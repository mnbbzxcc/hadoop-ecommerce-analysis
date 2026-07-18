import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8080/api',
    timeout: 10000,
});

export default {
    // 实时指标
    getTotalPV() {
        return api.get('/realtime/total-pv');
    },
    getMinutePV() {
        return api.get('/realtime/pv');
    },
    getMinuteUV() {
        return api.get('/realtime/uv');
    },
    getHotProducts(top = 10) {
        return api.get(`/realtime/hot?top=${top}`);
    },
    // 离线指标
    getDailyStats() {
        return api.get('/offline/daily-stats');
    },
    getHourlyStats(date) {
        return api.get(`/offline/hourly-stats?date=${date}`);
    },
    getTopProducts(date, top = 10) {
        return api.get(`/offline/top-products?date=${date}&top=${top}`);
    },
    getTopCategories(date, top = 10) {
        return api.get(`/offline/top-categories?date=${date}&top=${top}`);
    },
    getFunnel() {
        return api.get('/offline/funnel');
    }
};