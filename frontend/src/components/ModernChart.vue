<template>
  <v-card class="modern-chart-card" elevation="0" rounded="xl">
    <v-card-title class="chart-header">
      <div class="chart-title-section">
        <v-icon :color="iconColor" size="24" class="mr-3">{{ icon }}</v-icon>
        <span class="chart-title">{{ title }}</span>
      </div>
      <div class="chart-actions" v-if="showActions">
        <v-btn
          v-for="action in actions"
          :key="action.label"
          :color="action.color || 'primary'"
          variant="text"
          size="small"
          @click="action.onClick"
          class="action-btn"
        >
          {{ action.label }}
        </v-btn>
      </div>
    </v-card-title>
    
    <v-card-text class="chart-content">
      <!-- Chart Placeholder - You can integrate Chart.js, D3.js, or any charting library here -->
      <div class="chart-container" :style="{ height: height + 'px' }">
        <div class="chart-placeholder" v-if="!data || data.length === 0">
          <v-icon size="48" color="grey-lighten-2">mdi-chart-line</v-icon>
          <p class="text-grey mt-2">No data available</p>
        </div>
        <div v-else class="chart-data">
          <!-- Simple Bar Chart Implementation -->
          <div class="bar-chart" v-if="type === 'bar'">
            <div 
              v-for="(item, index) in data" 
              :key="index"
              class="bar-item"
            >
              <div class="bar-label">{{ item.label }}</div>
              <div class="bar-container">
                <div 
                  class="bar-fill"
                  :style="{ 
                    width: (item.value / maxValue) * 100 + '%',
                    backgroundColor: getBarColor(index)
                  }"
                ></div>
                <span class="bar-value">{{ item.value }}</span>
              </div>
            </div>
          </div>
          
          <!-- Simple Line Chart Implementation -->
          <div class="line-chart" v-else-if="type === 'line'">
            <svg :width="chartWidth" :height="chartHeight" class="line-svg">
              <polyline
                :points="linePoints"
                fill="none"
                :stroke="lineColor"
                stroke-width="3"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <circle
                v-for="(point, index) in linePointsArray"
                :key="index"
                :cx="point.x"
                :cy="point.y"
                :r="4"
                :fill="lineColor"
                class="line-point"
              />
            </svg>
          </div>
          
          <!-- Simple Pie Chart Implementation -->
          <div class="pie-chart" v-else-if="type === 'pie'">
            <svg :width="chartWidth" :height="chartHeight" class="pie-svg">
              <g transform="translate(100,100)">
                <path
                  v-for="(segment, index) in pieSegments"
                  :key="index"
                  :d="segment.path"
                  :fill="segment.color"
                  class="pie-segment"
                />
              </g>
            </svg>
            <div class="pie-legend">
              <div 
                v-for="(segment, index) in pieSegments"
                :key="index"
                class="legend-item"
              >
                <div 
                  class="legend-color"
                  :style="{ backgroundColor: segment.color }"
                ></div>
                <span class="legend-label">{{ segment.label }}</span>
                <span class="legend-value">{{ segment.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: 'mdi-chart-line'
  },
  iconColor: {
    type: String,
    default: 'primary'
  },
  type: {
    type: String,
    default: 'bar',
    validator: (value) => ['bar', 'line', 'pie'].includes(value)
  },
  data: {
    type: Array,
    default: () => []
  },
  height: {
    type: Number,
    default: 300
  },
  showActions: {
    type: Boolean,
    default: false
  },
  actions: {
    type: Array,
    default: () => []
  }
})

const chartWidth = 400
const chartHeight = 200

// Computed properties for chart rendering
const maxValue = computed(() => {
  return Math.max(...props.data.map(item => item.value))
})

const getBarColor = (index) => {
  const colors = ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']
  return colors[index % colors.length]
}

const lineColor = '#2563EB'

const linePoints = computed(() => {
  if (props.type !== 'line' || !props.data.length) return ''
  
  const points = props.data.map((item, index) => {
    const x = (index / (props.data.length - 1)) * chartWidth
    const y = chartHeight - (item.value / maxValue.value) * chartHeight
    return `${x},${y}`
  })
  
  return points.join(' ')
})

const linePointsArray = computed(() => {
  if (props.type !== 'line' || !props.data.length) return []
  
  return props.data.map((item, index) => {
    const x = (index / (props.data.length - 1)) * chartWidth
    const y = chartHeight - (item.value / maxValue.value) * chartHeight
    return { x, y }
  })
})

const pieSegments = computed(() => {
  if (props.type !== 'pie' || !props.data.length) return []
  
  const total = props.data.reduce((sum, item) => sum + item.value, 0)
  let currentAngle = 0
  
  return props.data.map((item, index) => {
    const percentage = item.value / total
    const angle = percentage * 360
    const startAngle = currentAngle
    const endAngle = currentAngle + angle
    
    currentAngle += angle
    
    const startAngleRad = (startAngle - 90) * (Math.PI / 180)
    const endAngleRad = (endAngle - 90) * (Math.PI / 180)
    
    const radius = 80
    const x1 = Math.cos(startAngleRad) * radius
    const y1 = Math.sin(startAngleRad) * radius
    const x2 = Math.cos(endAngleRad) * radius
    const y2 = Math.sin(endAngleRad) * radius
    
    const largeArcFlag = angle > 180 ? 1 : 0
    
    const path = `M 0,0 L ${x1},${y1} A ${radius},${radius} 0 ${largeArcFlag},1 ${x2},${y2} Z`
    
    return {
      path,
      color: getBarColor(index),
      label: item.label,
      value: item.value
    }
  })
})
</script>

<style scoped>
.modern-chart-card {
  background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.modern-chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.chart-header {
  background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding: 20px 24px;
}

.chart-title-section {
  display: flex;
  align-items: center;
}

.chart-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #0F172A;
}

.chart-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  font-size: 0.875rem;
  font-weight: 500;
}

.chart-content {
  padding: 24px;
}

.chart-container {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #94A3B8;
}

.chart-data {
  width: 100%;
  height: 100%;
}

/* Bar Chart Styles */
.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.bar-label {
  min-width: 80px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
}

.bar-container {
  flex: 1;
  position: relative;
  height: 24px;
  background: #F1F5F9;
  border-radius: 12px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 12px;
  transition: width 0.8s ease;
  position: relative;
}

.bar-value {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: #0F172A;
}

/* Line Chart Styles */
.line-svg {
  width: 100%;
  height: 100%;
}

.line-point {
  transition: all 0.3s ease;
}

.line-point:hover {
  r: 6;
  filter: drop-shadow(0 2px 4px rgba(37, 99, 235, 0.3));
}

/* Pie Chart Styles */
.pie-svg {
  width: 200px;
  height: 200px;
}

.pie-segment {
  transition: all 0.3s ease;
  cursor: pointer;
}

.pie-segment:hover {
  filter: brightness(1.1);
  transform: scale(1.05);
  transform-origin: center;
}

.pie-legend {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-label {
  flex: 1;
  font-size: 0.875rem;
  color: #475569;
}

.legend-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0F172A;
}

/* Responsive Design */
@media (max-width: 768px) {
  .chart-header {
    padding: 16px 20px;
  }
  
  .chart-content {
    padding: 20px;
  }
  
  .bar-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .bar-label {
    min-width: auto;
  }
}
</style>
