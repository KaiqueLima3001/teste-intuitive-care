<template>
  <div>
    <h1>Dashboard Gerencial</h1>

    <div v-if="loading" class="text-center">Carregando dados...</div>
    <div v-else-if="erro" class="error-msg">{{ erro }}</div>

    <div v-else-if="estatisticas" class="dashboard-container">
      
      <div class="kpi-row">
        <div class="card kpi-card">
          <h3>Total de Despesas</h3>
          <p class="big-number">R$ {{ formatarMoeda(estatisticas.total_despesas) }}</p>
        </div>
        <div class="card kpi-card">
          <h3>Média por Operadora</h3>
          <p class="big-number">R$ {{ formatarMoeda(estatisticas.media_despesas) }}</p>
        </div>
      </div>

      <div class="charts-row">
        
        <div class="card chart-section">
          <h3>Distribuição por UF</h3>
          
          <div class="canvas-wrapper" style="position: relative; height: 100%; min-height: 250px;">
            <canvas ref="graficoUF"></canvas>
          </div>
        </div>

        <div class="card table-section">
          <h3>Top 5 Operadoras</h3>
          <div class="table-wrapper mini-table">
            <table>
              <thead>
                <tr>
                  <th>Operadora</th>
                  <th class="text-right">Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(op, index) in estatisticas.top_5_operadoras" :key="index">
                  <td class="truncate" :title="op.razao_social">
                    {{ op.razao_social }}
                  </td>
                  <td class="text-right nowrap">
                    {{ formatarMoedaCompacta(op.total) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";
import { Chart } from "chart.js/auto";

export default {
  name: "Estatisticas",
  data() {
    return {
      estatisticas: null,
      loading: true,
      erro: null,
      meuGrafico: null
    };
  },
  async mounted() {
    try {
      const response = await api.getEstatisticas(); 
      this.estatisticas = response.data;
      
      // Verifica se temos dados para desenhar
      if (this.estatisticas.despesas_por_uf && this.estatisticas.despesas_por_uf.length > 0) {
        // setTimeout: garantir que o HTML está pronto
        setTimeout(() => {
            this.renderizarGrafico();
        }, 100); 
      }
      
    } catch (error) {
      console.error("Erro:", error);
      this.erro = "Erro ao carregar dados.";
    } finally {
      this.loading = false;
    }
  },
  methods: {
    renderizarGrafico() {
        if (!this.$refs.graficoUF) return;

        const dados = this.estatisticas.despesas_por_uf;
        
        // Destrói gráfico anterior para evitar bugs na navegação
        if (this.meuGrafico) this.meuGrafico.destroy();

        this.meuGrafico = new Chart(this.$refs.graficoUF, {
            type: "bar",
            data: {
                labels: dados.map(i => i.uf),
                datasets: [{
                    label: "Despesas",
                    data: dados.map(i => i.total),
                    backgroundColor: "#2563eb",
                    borderRadius: 4,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true },
                    x: { grid: { display: false } }
                }
            }
        });
    },
    formatarMoeda(valor) {
      if (!valor) return "0,00";
      return Number(valor).toLocaleString("pt-BR", { minimumFractionDigits: 2 });
    },
    formatarMoedaCompacta(valor) {
      if (!valor) return "0";
      return Number(valor).toLocaleString("pt-BR", { 
        style: 'currency', currency: 'BRL', maximumFractionDigits: 0 
      }); 
    }
  }
};
</script>

<style scoped>
/* Layout e Grid */
.dashboard-container { display: flex; flex-direction: column; gap: 1rem; }
.kpi-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.charts-row { display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; height: 320px; }

/* Cards */
.kpi-card { padding: 0.8rem 1.2rem; display: flex; justify-content: space-between; align-items: center; }
.kpi-card h3 { margin: 0; font-size: 0.9rem; }
.big-number { margin: 0; font-size: 1.4rem; color: #2563eb; }

/* Seções Internas */
.chart-section, .table-section { display: flex; flex-direction: column; overflow: hidden; }

/* Tabela */
.mini-table { margin-top: 0.5rem; border: none; box-shadow: none; overflow-y: auto; }
.mini-table th { padding: 0.5rem; font-size: 0.7rem; background: #f1f5f9; color: #64748b; }
.mini-table td { padding: 0.5rem; font-size: 0.75rem; }
.truncate { max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nowrap { white-space: nowrap; }

/* Responsividade */
@media (max-width: 768px) {
  .charts-row { grid-template-columns: 1fr; height: auto; }
  .canvas-wrapper { min-height: 250px; }
}
</style>