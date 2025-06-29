<template>
  <div class="chart-view-wrapper" :class="{ compressed: props.showChat }">
    <div class="chart-container-outer">
      <!-- Hover 資訊 -->
      <div class="hover-display" v-if="hoverData">
        <div class="ohlc">
          <div>{{ hoverData.date }}</div>
          <div>開盤：{{ hoverData.open.toFixed(2) }}</div>
          <div>最高：{{ hoverData.high.toFixed(2) }}</div>
          <div>最低：{{ hoverData.low.toFixed(2) }}</div>
          <div>收盤：
            <span :class="hoverData.close > hoverData.open ? 'up' : hoverData.close < hoverData.open ? 'down' : ''">
              {{ hoverData.close.toFixed(2) }}
            </span>
          </div>
        </div>

        <div class="extra-info">
          <div>
            成交量：
            <template v-if="props.type === 'stock'">
              {{ (hoverData.volume / 1e3).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }} 張
            </template>
            <template v-else>
              {{ (hoverData.volume / 1e6).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }} 百萬張
            </template>
          </div>

          <div>
            {{ props.type === 'stock' ? '成交金額' : '成交值' }}：
            <template v-if="props.type === 'stock'">
              {{ (hoverData.turnover / 1e3).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }} 千元
            </template>
            <template v-else>
              {{ (hoverData.turnover / 1e8).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }} 億元
            </template>
          </div>

          <div>
            漲跌點數：
            <span :class="hoverData.change_point > 0 ? 'up' : hoverData.change_point < 0 ? 'down' : ''">
              {{ hoverData.change_point.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </span>
          </div>

          <div>
            漲跌幅：
            <span :class="hoverData.change_percent > 0 ? 'up' : hoverData.change_percent < 0 ? 'down' : ''">
              {{ hoverData.change_percent.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}%
            </span>
          </div>
        </div>

        <div class="ma-values">
          <span :class="['ma-toggle-label', showMA5 ? 'active' : 'inactive']" style="color: #3b82f6" @click="showMA5 = !showMA5">MA5：{{ hoverData.ma5?.toFixed(2) ?? '-' }}</span>
          <span :class="['ma-toggle-label', showMA20 ? 'active' : 'inactive']" style="color: #a855f7" @click="showMA20 = !showMA20">MA20：{{ hoverData.ma20?.toFixed(2) ?? '-' }}</span>
          <span :class="['ma-toggle-label', showMA60 ? 'active' : 'inactive']" style="color: #f97316" @click="showMA60 = !showMA60">MA60：{{ hoverData.ma60?.toFixed(2) ?? '-' }}</span>
        </div>
      </div>

      <div ref="chartContainer" class="chart"></div>
    </div>
        <!-- 浮動留言按鈕 -->
    <button v-if="!props.showChat" class="chat-toggle-button" @click="$emit('open-chat')">留言</button>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { createChart, CandlestickSeries, LineSeries, HistogramSeries } from 'lightweight-charts'

defineEmits(['open-chat'])

const props = defineProps({
  candles: { type: Array, required: true },
  type: { type: String, default: 'stock' },
  showChat: { type: Boolean, default: false },
})

const chartContainer = ref(null)
const hoverData = ref(null)
const showMA5 = ref(true)
const showMA20 = ref(true)
const showMA60 = ref(true)
const isHovering = ref(false)

const updateHoverData = (data) => {
  const dt = new Date(data.time * 1000)
  hoverData.value = {
    date: dt.toLocaleDateString('zh-TW'),
    open: data.open,
    high: data.high,
    low: data.low,
    close: data.close,
    volume: data.volume,
    turnover: data.turnover,
    change_point: data.change_point,
    change_percent: data.change_percent,
    ma5: data.ma5,
    ma20: data.ma20,
    ma60: data.ma60,
  }
}

let chart = null
let candleSeries = null
let volumeSeries = null
let ma5Series = null
let ma20Series = null
let ma60Series = null
let resizeObserver = null

const updateMAVisibility = () => {
  ma5Series?.applyOptions({ visible: showMA5.value })
  ma20Series?.applyOptions({ visible: showMA20.value })
  ma60Series?.applyOptions({ visible: showMA60.value })
}

const initChart = () => {
  const width = chartContainer.value.clientWidth
  const height = chartContainer.value.clientHeight
  if (!width || !height) return

  chart = createChart(chartContainer.value, {
    width,
    height,
    layout: { background: { color: '#0d1117' }, textColor: '#e6edf3' },
    grid: {
      vertLines: { color: '#30363d' },
      horzLines: { color: '#30363d' },
    },
    timeScale: {
      timeVisible: true,
      rightOffset: 5,
      barSpacing: 14,
      fixRightEdge: true,
      fixLeftEdge: true, // 加這行防止左邊滑出空白
    },
    crosshair: {
      mode: 0,
      vertLine: { visible: true, labelVisible: false },
      horzLine: { visible: true },
    },
  })

  candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#ef5350',
    downColor: '#26a69a',
    borderVisible: false,
    wickUpColor: '#ef5350',
    wickDownColor: '#26a69a',
  })
  candleSeries.setData(props.candles)

  volumeSeries = chart.addSeries(HistogramSeries, {
    priceScaleId: 'volume',
    priceFormat: {
      type: 'custom',
      formatter: () => '', // 不顯示任何數字
    },
    lastValueVisible: false, // 隱藏紅色標籤數字
    scaleMargins: { top: 0.8, bottom: 0 },
  })

  volumeSeries.setData(props.candles.map(c => ({
    time: c.time,
    value: c.volume || 0,
    color: c.close >= c.open ? '#ef5350' : '#26a69a',
  })))
  chart.priceScale('volume').applyOptions({
    scaleMargins: { top: 0.84, bottom: 0 },
    borderVisible: false,
    tickMarkFormatter: val => `${val.toFixed(0)} 張`,
  })

  chart.priceScale('right').applyOptions({
    scaleMargins: { top: 0.05, bottom: 0.25 },
  })

  const maCommon = {
    lineWidth: 1.5,
    lastValueVisible: false,
    priceLineVisible: false,
  }

  ma5Series = chart.addSeries(LineSeries, { color: '#3b82f6', visible: showMA5.value, ...maCommon })
  ma20Series = chart.addSeries(LineSeries, { color: '#a855f7', visible: showMA20.value, ...maCommon })
  ma60Series = chart.addSeries(LineSeries, { color: '#f97316', visible: showMA60.value, ...maCommon })

  ma5Series.setData(props.candles.filter(c => c.ma5).map(c => ({ time: c.time, value: c.ma5 })))
  ma20Series.setData(props.candles.filter(c => c.ma20).map(c => ({ time: c.time, value: c.ma20 })))
  ma60Series.setData(props.candles.filter(c => c.ma60).map(c => ({ time: c.time, value: c.ma60 })))

  chart.timeScale().scrollToPosition(props.candles.length - 1, false)

  chart.subscribeCrosshairMove(param => {
    const point = param?.point
    const ohlc = param?.seriesData?.get(candleSeries)
    if (!point || !param?.time || !ohlc) {
      isHovering.value = false
      const latest = props.candles.at(-1)
      if (latest) updateHoverData({ ...latest, time: latest.time })
      return
    }
    isHovering.value = true
    const index = props.candles.findIndex(c => c.time === param.time)
    const current = props.candles[index]
    if (!current) return
    updateHoverData({
      time: param.time,
      open: ohlc.open,
      high: ohlc.high,
      low: ohlc.low,
      close: ohlc.close,
      volume: current.volume,
      turnover: current.turnover,
      change_point: current.change_point,
      change_percent: current.change_percent,
      ma5: current.ma5,
      ma20: current.ma20,
      ma60: current.ma60,
    })
  })
}

onMounted(async () => {
  await nextTick()
  if (props.candles.length > 0) {
    const latest = props.candles.at(-1)
    updateHoverData({ ...latest, time: latest.time })
  }

  resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
      const width = entry.contentRect.width
      const height = entry.contentRect.height
      if (width > 0 && height > 0) {
        if (!chart) initChart()
        else chart.resize(width, height)
      }
    }
  })
  resizeObserver.observe(chartContainer.value)
  watch([showMA5, showMA20, showMA60], updateMAVisibility)
})

onUnmounted(() => {
  resizeObserver?.disconnect()
})
</script>

<style scoped>
.chart-view-wrapper {
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  position: relative;
}

.chart-container-outer {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background-color: #0d1117;
  padding: 0.5rem;
  border-radius: 12px;
  border: 1px solid #30363d;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.chart {
  flex: 1;
  min-height: 0;
  width: 100%;
  border-radius: 8px;
  box-shadow: inset 0 0 0 1px #2c313a;
  position: relative;
}

.hover-display {
  font-size: 13px;
  color: #e6edf3;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  align-items: flex-start;
  margin-left: 0.2rem;
}

.extra-info,
.ohlc,
.ma-values {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.hover-display span.up {
  color: #ef5350;
}

.hover-display span.down {
  color: #26a69a;
}

.ma-values {
  display: flex;
  gap: 0.5rem;
  font-size: 0.9rem;
  user-select: none;
}

.ma-toggle-label {
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.2s ease;
}

.ma-toggle-label.active {
  opacity: 1;
  text-decoration: none;
}

.ma-toggle-label.inactive {
  opacity: 0.3;
  text-decoration: line-through;
}

.chat-toggle-button {
  position: absolute;
  top: 10px;
  right: 12px;
  background-color: #40f907b3;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  z-index: 10;
  font-size: 1rem;
  opacity: 0.9;
}

@media (max-width: 756px) {
  .chart-view-wrapper.compressed {
    height: 48vh;
  }
  .chat-toggle-button {
    top: auto;
    bottom: 12px;
    right: 12px;
    border-radius: 999px;
    font-size: 1rem;
    padding: 0.5rem 1rem;
  }
}
</style>

