<template>
  <div class="dashboard">
    <h1>电商用户行为分析系统</h1>

    <!-- 选项卡 -->
    <div class="tabs">
      <button 
        :class="{ active: activeTab === 'realtime' }" 
        @click="activeTab = 'realtime'">
        实时监控
      </button>
      <button 
        :class="{ active: activeTab === 'offline' }" 
        @click="activeTab = 'offline'">
        离线分析
      </button>
    </div>

    <!-- 实时监控面板 -->
    <div v-show="activeTab === 'realtime'" class="tab-panel">
      <div class="stats-row">
        <div class="stat-card">
          <h3>累计 PV</h3>
          <div class="value">{{ totalPV }}</div>
        </div>
        <div class="stat-card">
          <h3>最近1分钟 PV</h3>
          <div class="value">{{ minutePV }}</div>
        </div>
        <div class="stat-card">
          <h3>最近1分钟 UV</h3>
          <div class="value">{{ minuteUV }}</div>
        </div>
      </div>
      <div class="stats-row">
        <div class="stat-card full-width">
          <h3>热门商品 Top 5（最近5分钟）</h3>
          <ol>
            <li v-for="item in hotProducts" :key="item.value">
              {{ item.value }} ({{ item.score }})
            </li>
          </ol>
        </div>
      </div>
    </div>

    <!-- 离线分析面板 -->
    <div v-show="activeTab === 'offline'" class="tab-panel">
      <!-- 第一行：每日 PV/UV 趋势 -->
      <div class="chart-row">
        <div class="chart-card full-width">
          <h3>每日 PV/UV 趋势</h3>
          <div ref="trendChartRef" style="width: 100%; height: 400px;"></div>
        </div>
      </div>

      <!-- 第二行：每小时 PV/UV 趋势 -->
      <div class="chart-row">
        <div class="chart-card full-width">
          <h3>每小时 PV/UV 趋势（最近一天）</h3>
          <div ref="hourlyChartRef" style="width: 100%; height: 400px;"></div>
        </div>
      </div>

      <!-- 第三行：行为分布 + 转化漏斗 -->
      <div class="stats-row">
        <div class="stat-card half">
          <h3>行为分布（最近一天）</h3>
          <div ref="behaviorChartRef" style="width: 100%; height: 400px;"></div>
        </div>
        <div class="stat-card half">
          <h3>转化漏斗（最近一天）</h3>
          <div ref="funnelChartRef" style="width: 100%; height: 400px;"></div>
        </div>
      </div>

      <!-- 第四行：热门商品 + 热门类目 -->
      <div class="stats-row">
        <div class="stat-card half">
          <h3>热门商品 Top 10（最近一天）</h3>
          <ol>
            <li v-for="item in topProducts" :key="item.product_id">
              {{ item.product_id }} ({{ item.pv }})
            </li>
          </ol>
        </div>
        <div class="stat-card half">
          <h3>热门类目 Top 10（最近一天）</h3>
          <ol>
            <li v-for="item in topCategories" :key="item.category_id">
              {{ item.category_id }} ({{ item.pv }})
            </li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import * as echarts from 'echarts';
import api from './api';

// 实时数据
const totalPV = ref('--');
const minutePV = ref('--');
const minuteUV = ref('--');
const hotProducts = ref([]);

// 离线数据
const dailyStats = ref([]);
const hourlyStats = ref([]);
const topProducts = ref([]);
const topCategories = ref([]);
const funnelData = ref([]);

// 图表 DOM 引用
const trendChartRef = ref(null);
const behaviorChartRef = ref(null);
const hourlyChartRef = ref(null);
const funnelChartRef = ref(null);
let trendChart = null;
let behaviorChart = null;
let hourlyChart = null;
let funnelChart = null;

// 标记离线图表是否已初始化
let offlineChartsInitialized = false;

// 选项卡状态
const activeTab = ref('realtime');

// 定时器
let realtimeInterval = null;

// 获取实时数据
const fetchRealtime = async () => {
  try {
    const totalPVRes = await api.getTotalPV();
    totalPV.value = totalPVRes.data;
    const minutePVRes = await api.getMinutePV();
    minutePV.value = minutePVRes.data;
    const minuteUVRes = await api.getMinuteUV();
    minuteUV.value = minuteUVRes.data;
    const hotRes = await api.getHotProducts(5);
    hotProducts.value = hotRes.data;
  } catch (error) {
    console.error('实时数据获取失败', error);
  }
};

// 获取每日统计并绘制图表
const fetchDailyStats = async () => {
  try {
    const res = await api.getDailyStats();
    dailyStats.value = res.data;
    if (dailyStats.value.length === 0) return;
    
    if (offlineChartsInitialized && activeTab.value === 'offline') {
      updateTrendChart();
      updateBehaviorChart();
    }
  } catch (error) {
    console.error('每日统计获取失败', error);
  }
};

// 更新每日趋势图
const updateTrendChart = () => {
  if (!trendChart || dailyStats.value.length === 0) return;
  const dates = dailyStats.value.map(item => item.dt);
  const pvData = dailyStats.value.map(item => item.pv);
  const uvData = dailyStats.value.map(item => item.uv);
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['PV', 'UV'], left: 'center', top: 0 },
    grid: { left: '5%', right: '3%', top: '15%', bottom: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45, interval: 0, fontSize: 11, margin: 15 }
    },
    yAxis: { type: 'value', name: '数量' },
    series: [
      { name: 'PV', type: 'line', data: pvData, smooth: true, areaStyle: { opacity: 0.1 } },
      { name: 'UV', type: 'line', data: uvData, smooth: true, areaStyle: { opacity: 0.1 } }
    ]
  });
  trendChart.resize();
};

// 更新行为分布图
const updateBehaviorChart = () => {
  if (!behaviorChart || dailyStats.value.length === 0) return;
  const lastDay = dailyStats.value[dailyStats.value.length - 1];
  const behaviorData = [
    { name: 'pv', value: lastDay.pv_count },
    { name: 'buy', value: lastDay.buy_count },
    { name: 'cart', value: lastDay.cart_count },
    { name: 'fav', value: lastDay.fav_count }
  ];
  behaviorChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', data: behaviorData.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      data: behaviorData,
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 }
    }]
  });
  behaviorChart.resize();
};

// 获取最近一天的每小时统计
const fetchHourlyStats = async () => {
  try {
    if (dailyStats.value.length === 0) return;
    const lastDate = dailyStats.value[dailyStats.value.length - 1].dt;
    const res = await api.getHourlyStats(lastDate);
    hourlyStats.value = res.data;
    if (hourlyStats.value.length === 0) return;
    
    if (offlineChartsInitialized && activeTab.value === 'offline') {
      updateHourlyChart();
    }
  } catch (error) {
    console.error('每小时统计获取失败', error);
  }
};

// 更新每小时趋势图
const updateHourlyChart = () => {
  if (!hourlyChart || hourlyStats.value.length === 0) return;
  const hours = hourlyStats.value.map(item => item.hour);
  const pvData = hourlyStats.value.map(item => item.pv);
  const uvData = hourlyStats.value.map(item => item.uv);
  hourlyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['PV', 'UV'], left: 'center', top: 0 },
    grid: { left: '5%', right: '3%', top: '15%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: hours, name: '小时' },
    yAxis: { type: 'value', name: '数量' },
    series: [
      { name: 'PV', type: 'line', data: pvData, smooth: true },
      { name: 'UV', type: 'line', data: uvData, smooth: true }
    ]
  });
  hourlyChart.resize();
};

// 获取最近一天的热门商品和类目
const fetchTopProductsAndCategories = async () => {
  try {
    if (dailyStats.value.length === 0) return;
    const lastDate = dailyStats.value[dailyStats.value.length - 1].dt;
    const productsRes = await api.getTopProducts(lastDate, 10);
    topProducts.value = productsRes.data;
    const categoriesRes = await api.getTopCategories(lastDate, 10);
    topCategories.value = categoriesRes.data;
  } catch (error) {
    console.error('热门商品/类目获取失败', error);
  }
};

// 获取最近一天的转化漏斗
const fetchFunnel = async () => {
  try {
    const res = await api.getFunnel();
    funnelData.value = res.data;
    if (funnelData.value.length === 0) return;
    
    if (offlineChartsInitialized && activeTab.value === 'offline') {
      updateFunnelChart();
    }
  } catch (error) {
    console.error('转化漏斗获取失败', error);
  }
};

// 更新漏斗图
const updateFunnelChart = () => {
  if (!funnelChart || funnelData.value.length === 0) return;
  const lastFunnel = funnelData.value[funnelData.value.length - 1];
  const funnelSeries = [
    { name: 'PV 用户', value: lastFunnel.pv_uv },
    { name: '加购用户', value: lastFunnel.cart_uv },
    { name: '购买用户', value: lastFunnel.buy_uv }
  ];
  funnelChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'funnel',
      data: funnelSeries,
      label: { show: true, position: 'inside' },
      itemStyle: { borderColor: '#fff', borderWidth: 2 }
    }]
  });
  funnelChart.resize();
};

// 初始化所有离线图表（仅在可见时调用）
const initOfflineCharts = () => {
  if (offlineChartsInitialized) return;
  if (!trendChartRef.value || !behaviorChartRef.value || !hourlyChartRef.value || !funnelChartRef.value) return;
  
  const checkAndInit = () => {
    if (trendChartRef.value.clientWidth === 0) {
      setTimeout(checkAndInit, 100);
      return;
    }
    trendChart = echarts.init(trendChartRef.value);
    behaviorChart = echarts.init(behaviorChartRef.value);
    hourlyChart = echarts.init(hourlyChartRef.value);
    funnelChart = echarts.init(funnelChartRef.value);
    offlineChartsInitialized = true;
    
    updateTrendChart();
    updateBehaviorChart();
    updateHourlyChart();
    updateFunnelChart();
    
    nextTick(() => {
      if (trendChart) trendChart.resize();
      if (behaviorChart) behaviorChart.resize();
      if (hourlyChart) hourlyChart.resize();
      if (funnelChart) funnelChart.resize();
    });
  };
  
  checkAndInit();
};

// 窗口自适应
const handleResize = () => {
  if (trendChart) trendChart.resize();
  if (behaviorChart) behaviorChart.resize();
  if (hourlyChart) hourlyChart.resize();
  if (funnelChart) funnelChart.resize();
};

onMounted(() => {
  // 加载实时数据
  fetchRealtime();
  
  // 加载离线数据
  fetchDailyStats().then(() => {
    fetchHourlyStats();
    fetchTopProductsAndCategories();
  });
  fetchFunnel();
  
  // 如果初始选项卡就是离线，则立即初始化图表
  if (activeTab.value === 'offline') {
    nextTick(() => initOfflineCharts());
  }
  
  // 定时刷新实时数据
  realtimeInterval = setInterval(fetchRealtime, 10000);
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize);
});

// 监听选项卡切换
watch(activeTab, (newVal) => {
  if (newVal === 'offline') {
    if (!offlineChartsInitialized) {
      nextTick(() => initOfflineCharts());
    } else {
      nextTick(() => handleResize());
    }
  }
});

onUnmounted(() => {
  if (realtimeInterval) clearInterval(realtimeInterval);
  window.removeEventListener('resize', handleResize);
  if (trendChart) trendChart.dispose();
  if (behaviorChart) behaviorChart.dispose();
  if (hourlyChart) hourlyChart.dispose();
  if (funnelChart) funnelChart.dispose();
});
</script>

<style>
/* 强制所有祖先元素占满全宽 */
html, body, #app {
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  max-width: 100% !important;
  overflow-x: hidden;
  display: block !important;
}

/* 强制 .dashboard 占满父容器 */
.dashboard {
  width: 100% !important;
  max-width: 100% !important;
  margin: 0 !important;
  padding: 20px !important;
  box-sizing: border-box !important;
}

/* 全局盒模型重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>

<style scoped>
.dashboard {
  width: 100%;
  padding: 20px;
  font-family: 'Segoe UI', 'PingFang SC', Roboto, sans-serif;
  background: #f0f2f5;
  min-height: 100vh;
  box-sizing: border-box;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.8rem;
  color: #1f2f3a;
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.tabs button {
  padding: 8px 20px;
  font-size: 1rem;
  border: none;
  background: #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.tabs button.active {
  background: #42b983;
  color: white;
  box-shadow: 0 2px 8px rgba(66,185,131,0.3);
}

.tab-panel {
  animation: fade 0.3s;
}

@keyframes fade {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1 1 200px;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

.stat-card.full-width {
  flex: 1 1 100%;
}

.stat-card.half {
  flex: 1 1 300px;
}

.stat-card .value {
  font-size: 2rem;
  font-weight: bold;
  color: #42b983;
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: #666;
  font-weight: 500;
  text-align: center;
}

.chart-card.full-width {
  flex: 1 1 100%;
}

.stat-card.half {
  flex: 1 1 calc(50% - 20px);
  min-width: 300px;
}

.chart-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  flex: 1;
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
  width: 100%;
}

.chart-card h3 {
  margin: 0 0 12px 0;
  font-size: 1rem;
  color: #666;
  text-align: center;
}

.chart-card div {
  width: 100% !important;
  height: 400px;
}

ol {
  padding-left: 20px;
  margin: 0;
}

li {
  margin: 6px 0;
  font-size: 0.9rem;
  color: #555;
}

@media (max-width: 768px) {
  .stats-row, .chart-row {
    flex-direction: column;
  }
  .stat-card, .chart-card {
    flex: 1 1 auto;
  }
}
</style>