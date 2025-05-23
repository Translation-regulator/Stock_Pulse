<template>
  <div class="chart-view-wrapper">
    <div class="chart-container-outer">
      <!-- Hover 資訊 -->
      <div class="hover-display" v-if="hoverData">
        <div class="ohlc">
          <div>{{ hoverData.date }}</div>
          <div>開盤：{{ hoverData.open.toFixed(2) }}</div>
          <div>最高：{{ hoverData.high.toFixed(2) }}</div>
          <div>最低：{{ hoverData.low.toFixed(2) }}</div>
          <div>收盤：
            <span :class="hoverData.close > hoverData.open ? 'up' : 'down'">
              {{ hoverData.close.toFixed(2) }}
            </span>
          </div>
        </div>

        <div class="extra-info">
          <div>成交量：{{ (hoverData.volume / 1e6).toFixed(2) }} 張</div>
          <div>成交金額：{{ (hoverData.turnover / 1e3).toFixed(2) }} 千元</div>
          <div>漲跌點數：
            <span :class="hoverData.change_point > 0 ? 'up' : 'down'">
              {{ hoverData.change_point.toFixed(2) }}
            </span>
          </div>
          <div>漲跌幅：
            <span :class="hoverData.change_percent > 0 ? 'up' : 'down'">
              {{ hoverData.change_percent.toFixed(2) }}%
            </span>
          </div>
        </div>

        <!-- MA 數值 + 按下切換顯示 -->
        <div class="ma-values">
          <span
            :class="['ma-toggle-label', showMA5 ? 'active' : 'inactive']"
            style="color: #3b82f6"
            @click="showMA5 = !showMA5"
          >
            MA5：{{ hoverData.ma5?.toFixed(2) ?? '-' }}
          </span>
          <span
            :class="['ma-toggle-label', showMA20 ? 'active' : 'inactive']"
            style="color: #a855f7"
            @click="showMA20 = !showMA20"
          >
            MA20：{{ hoverData.ma20?.toFixed(2) ?? '-' }}
          </span>
          <span
            :class="['ma-toggle-label', showMA60 ? 'active' : 'inactive']"
            style="color: #f97316"
            @click="showMA60 = !showMA60"
          >
            MA60：{{ hoverData.ma60?.toFixed(2) ?? '-' }}
          </span>
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
      rightOffset: 5,
      barSpacing: 14,
      fixRightEdge: true,
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
    priceFormat: { type: 'volume' },
    scaleMargins: { top: 0.8, bottom: 0 },
  })
  volumeSeries.setData(
    props.candles.map(c => ({
      time: c.time,
      value: c.volume || 0,
      color: c.close >= c.open ? '#ef5350' : '#26a69a',
    }))
  )

  chart.priceScale('volume').applyOptions({
    scaleMargins: { top: 0.84, bottom: 0 },
    borderVisible: false,
    tickMarkFormatter: val => `${val.toFixed(0)} 張`,
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

  chart.subscribeCrosshairMove(param => {
    const ohlc = param?.seriesData?.get(candleSeries)
    const index = props.candles.findIndex(c => c.time === param?.time)
    const current = props.candles[index]
    const prev = props.candles[index - 1] ?? {}

    if (ohlc && current) {
      const dt = new Date(typeof param.time === 'object' && 'timestamp' in param.time ? param.time.timestamp * 1000 : param.time * 1000)
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
      }
    }
  })
}

onMounted(() => {
  resizeObserver = new ResizeObserver(entries => {
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
  height: calc(100vh - 140px);
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
.hover-display {
  font-size: 1.2rem;
  color: #e6edf3;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  align-items: flex-start;
  margin-left: 0.2rem;
}
.extra-info, .ohlc, .ma-values {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
}
.hover-display span.up {
  color: #ef5350;
}
.hover-display span.down {
  color: #26a69a;
}
.ma-values {
  display: flex;
  gap: 1.5rem;
  font-size: 1.1rem;
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
</style>
