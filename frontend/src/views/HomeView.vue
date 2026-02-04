<template>
  <div class="home">
    <h1>Painel de Operadoras</h1>
    
    <div class="search-box">
      <input 
        v-model="search" 
        @keyup.enter="carregarOperadoras" 
        placeholder="Buscar por Razão Social ou CNPJ..."
      >
      <button @click="carregarOperadoras">Pesquisar</button>
    </div>

    <div class="stats-section" v-if="estatisticas">
        <UfChart :operadorasData="estatisticas.top_5_operadoras" />
    </div>

    <table class="operadoras-table">
      <thead>
        <tr>
          <th>Registro ANS</th>
          <th>CNPJ</th>
          <th>Razão Social</th>
          <th>UF</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="op in operadoras" :key="op.registro">
          <td>{{ op.registro }}</td>
          <td>{{ op.cnpj }}</td>
          <td>{{ op.razao_social }}</td>
          <td>{{ op.uf }}</td>
          <td>
            <router-link :to="`/operadora/${op.cnpj}`" class="btn-detalhes">Ver Detalhes</router-link>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="pagination">
      <button :disabled="page <= 1" @click="mudarPagina(-1)">Anterior</button>
      <span>Página {{ page }} de {{ totalPaginas }}</span>
      <button :disabled="page >= totalPaginas" @click="mudarPagina(1)">Próxima</button>
    </div>
  </div>
</template>

<script>
import api from '../services/api';
import UfChart from '../components/UfChart.vue';

export default {
  components: { UfChart },
  data() {
    return {
      operadoras: [],
      estatisticas: null,
      search: '',
      page: 1,
      limit: 10,
      total: 0
    };
  },
  computed: {
    totalPaginas() {
      return Math.ceil(this.total / this.limit);
    }
  },
  methods: {
    async carregarOperadoras() {
      try {
        const response = await api.getOperadoras(this.page, this.limit, this.search);
        this.operadoras = response.data.data;
        this.total = response.data.total;
      } catch (error) {
        alert('Erro ao carregar operadoras');
      }
    },
    async carregarEstatisticas() {
        try {
            const response = await api.getEstatisticas();
            this.estatisticas = response.data;
        } catch (error) {
            console.error("Erro ao carregar estatísticas");
        }
    },
    mudarPagina(delta) {
      this.page += delta;
      this.carregarOperadoras();
    }
  },
  mounted() {
    this.carregarOperadoras();
    this.carregarEstatisticas();
  }
};
</script>

<style scoped>

/* layout das tabelas */
.operadoras-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
.operadoras-table th, .operadoras-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
.btn-detalhes { color: blue; text-decoration: underline; cursor: pointer; }
.search-box { margin-bottom: 20px; }
.pagination { margin-top: 20px; display: flex; gap: 10px; justify-content: center; }
</style>