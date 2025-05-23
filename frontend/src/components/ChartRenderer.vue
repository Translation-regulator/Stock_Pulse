<template>
  <div class="chart-view-wrapper">
    <div class="chart-container-outer">
      <!-- 點擊圖例切換 MA -->
      <div class="ma-toggle">
        <span @click="showMA5 = !showMA5" :class="['ma-label', showMA5 ? 'active' : '']" style="color: #3b82f6;">MA5</span>
        <span @click="showMA20 = !showMA20" :class="['ma-label', showMA20 ? 'active' : '']" style="color: #a855f7;">MA20</span>
        <span @click="showMA60 = !showMA60" :class="['ma-label', showMA60 ? 'active' : '']" style="color: #f97316;">MA60</span>
      </div>

      <!-- Hover 資訊 -->
      <div class="hover-display" v-if="hoverData">
        <div class="ohlc">
          <div>{{ hoverData.date }}</div>
          <div>開盤：{{ hoverData.open }}</div>
          <div>最高：{{ hoverData.high }}</div>
          <div>最低：{{ hoverData.low }}</div>
          <div>收盤：<span :class="hoverData.close > hoverData.open ? 'up' : 'down'">{{ hoverData.close }}</span></div>
        </div>

        <div class="extra-info">
          <div>成交量：{{ (hoverData.volume / 1000).toLocaleString() }} 張</div>
          <div>成交金額：{{ hoverData.turnover?.toLocaleString() }} 元</div>
          <div>漲跌點數：<span :class="hoverData.change_point > 0 ? 'up' : 'down'">{{ hoverData.change_point }}</span></div>
          <div>漲跌幅：<span :class="hoverData.change_percent > 0 ? 'up' : 'down'">{{ hoverData.change_percent }}%</span></div>
        </div>

        <div class="ma-values">
          <div v-if="hoverData.ma5 !== undefined"><span style="color: #3b82f6;">MA5：</span><span :class="hoverData.ma5Color">{{ hoverData.ma5 }}</span></div>
          <div v-if="hoverData.ma20 !== undefined"><span style="color: #a855f7;">MA20：</span><span :class="hoverData.ma20Color">{{ hoverData.ma20 }}</span></div>
          <div v-if="hoverData.ma60 !== undefined"><span style="color: #f97316;">MA60：</span><span :class="hoverData.ma60Color">{{ hoverData.ma60 }}</span></div>
        </div>
      </div>

      <div ref="chartContainer" class="chart"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, onUnmounted } from 'vue'
import { createChart, CandlestickSeries, LineSeries, HistogramSeries } from 'lightweight-charts'

const props = defineProps({
  candles: { type: Array, required: true },
})

const chartContainer = ref(null)
const hoverData = ref(null)

let chart = null
let candleSeries = null
let volumeSeries = null
let ma5Series = null
let ma20Series = null
let ma60Series = null
let resizeObserver = null

const showMA5 = ref(true)
const showMA20 = ref(true)
const showMA60 = ref(true)

const updateMAVisibility = () => {
  ma5Series?.applyOptions({ visible: showMA5.value })
  ma20Series?.applyOptions({ visible: showMA20.value })
  ma60Series?.applyOptions({ visible: showMA60.value })
}

const initChart = () => {
  const width = chartContainer.value.clientWidth || 800
  const height = chartContainer.value.clientHeight || 500

  chart = createChart(chartContainer.value, {
    width,
    height,
    layout: {
      background: { color: '#0d1117' },
      textColor: '#e6edf3',
    },
    grid: {
      vertLines: { color: '#30363d' },
      horzLines: { color: '#30363d' },
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
      overlay: true,
      rightOffset: 5,
      barSpacing: 14,
      fixRightEdge: true,
      tickMarkFormatter: (time) => {
        const ts = typeof time === 'object' && 'timestamp' in time ? time.timestamp : time
        const date = new Date(ts * 1000)
        const y = date.getFullYear()
        const m = (date.getMonth() + 1).toString().padStart(2, '0')
        const d = date.getDate().toString().padStart(2, '0')
        return `${y}/${m}/${d}`
      }
    },
    crosshair: {
      mode: 0,
      vertLine: { visible: true, labelVisible: false },
      horzLine: { visible: true }
    }
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
    priceFormat: { type: 'volume' },
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
    tickMarkFormatter: (val) => `${val.toFixed(0)} 張`,
  })

  chart.priceScale('right').applyOptions({
    scaleMargins: { top: 0.05, bottom: 0.25 },
  })

  const maCommonOpts = {
    lineWidth: 1.5,
    lastValueVisible: false,
    priceLineVisible: false,
  }

  ma5Series = chart.addSeries(LineSeries, { color: '#3b82f6', visible: showMA5.value, ...maCommonOpts })
  ma20Series = chart.addSeries(LineSeries, { color: '#a855f7', visible: showMA20.value, ...maCommonOpts })
  ma60Series = chart.addSeries(LineSeries, { color: '#f97316', visible: showMA60.value, ...maCommonOpts })

  ma5Series.setData(props.candles.map(c => c.ma5 ? { time: c.time, value: c.ma5 } : null).filter(Boolean))
  ma20Series.setData(props.candles.map(c => c.ma20 ? { time: c.time, value: c.ma20 } : null).filter(Boolean))
  ma60Series.setData(props.candles.map(c => c.ma60 ? { time: c.time, value: c.ma60 } : null).filter(Boolean))

  chart.timeScale().scrollToPosition(props.candles.length - 1, false)

  chart.subscribeCrosshairMove((param) => {
    const ohlc = param?.seriesData?.get(candleSeries)
    const index = props.candles.findIndex(c => c.time === param?.time)
    const current = props.candles[index]
    const prev = props.candles[index - 1] ?? {}

    if (ohlc && current) {
      const dt = typeof param.time === 'object' && 'timestamp' in param.time
        ? new Date(param.time.timestamp * 1000)
        : new Date(param.time * 1000)

      hoverData.value = {
        date: dt.toLocaleDateString('zh-TW'),
        open: ohlc.open,
        high: ohlc.high,
        low: ohlc.low,
        close: ohlc.close,
        volume: current.volume,
        turnover: current.turnover,
        change_point: current.change_point,
        change_percent: current.change_percent,
        ma5: current.ma5 ?? undefined,
        ma20: current.ma20 ?? undefined,
        ma60: current.ma60 ?? undefined,
        ma5Color: current.ma5 !== undefined && prev.ma5 !== undefined ? (current.ma5 > prev.ma5 ? 'up' : 'down') : '',
        ma20Color: current.ma20 !== undefined && prev.ma20 !== undefined ? (current.ma20 > prev.ma20 ? 'up' : 'down') : '',
        ma60Color: current.ma60 !== undefined && prev.ma60 !== undefined ? (current.ma60 > prev.ma60 ? 'up' : 'down') : '',
      }
    }
  })
}

onMounted(() => {
  resizeObserver = new ResizeObserver((entries) => {
    for (const entry of entries) {
      if (entry.contentRect.width > 0 && !chart) initChart()
      chart?.resize(entry.contentRect.width, chartContainer.value.clientHeight)
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
  height: calc(100vh - 60px - 40px);
  display: flex;
  flex-direction: column;
}

.chart-container-outer {
  background-color: #0d1117;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid #30363d;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  position: relative;
}

.chart {
  width: 100%;
  flex: 1;
  border-radius: 8px;
  box-shadow: inset 0 0 0 1px #2c313a;
  overflow: hidden;
}

.chart-contained canvas {
  max-width: 100% !important;
  height: auto !important;
  object-fit: contain;
}

.hover-display {
  font-size: 1.2rem;
  color: #e6edf3;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  align-items: flex-start;
  margin-left: 0.2rem;
}

.extra-info, .ohlc, .ma-values {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.hover-display span.up {
  color: #ef5350;
}
.hover-display span.down {
  color: #26a69a;
}

.ma-toggle {
  gap: 1.5rem;
  font-size: 0.95rem;
  user-select: none;
}
.ma-label {
  padding-right: 20px;
  cursor: pointer;
  opacity: 0.7;
}
.ma-label.active {
  font-weight: bold;
  text-decoration: underline;
  opacity: 1;
}
</style>