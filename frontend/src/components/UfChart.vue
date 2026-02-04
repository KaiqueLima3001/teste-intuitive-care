<template>
  <div class="chart-container">
    <h3>Distribuição de Despesas por UF (Top 5)</h3>
    <Bar v-if="loaded" :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export default {
  name: 'UfChart',
  components: { Bar },
  props: {
    operadorasData: Array 
  },
  data() {
    return {
      loaded: false,
      chartData: null,
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false
      }
    }
  },
  watch: {
    operadorasData: {
      immediate: true,
      handler(newData) {
        if (newData && newData.length > 0) {
          this.chartData = {
            labels: newData.map(item => item.uf),
            datasets: [
              {
                label: 'Total de Despesas (R$)',
                backgroundColor: '#42b983',
                data: newData.map(item => item.total_despesas)
              }
            ]
          }
          this.loaded = true
        }
      }
    }
  }
}
</script>

<style scoped>
.chart-container {
  height: 300px;
  margin: 20px 0;
}
</style>