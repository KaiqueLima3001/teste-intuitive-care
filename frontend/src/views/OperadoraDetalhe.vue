<template>
  <div class="detalhes-container" v-if="operadora">
    <button @click="$router.push('/')" class="btn-voltar">◀ Voltar</button>

    <div class="card-info">
      <h1>{{ operadora.razao_social }}</h1>
      <p><strong>CNPJ:</strong> {{ operadora.cnpj }}</p>
      <p><strong>Registro ANS:</strong> {{ operadora.registro }}</p>
      <p><strong>Modalidade:</strong> {{ operadora.modalidade }}</p>
      <p><strong>UF:</strong> {{ operadora.uf }}</p>
    </div>

    <div class="historico-section">
      <h2>Histórico de Despesas Assistenciais</h2>
      
      <div v-if="loading" class="loading">Carregando despesas...</div>
      
      <table v-else-if="despesas.length > 0" class="tabela-despesas">
        <thead>
          <tr>
            <th>Ano</th>
            <th>Trimestre</th>
            <th>Valor (R$)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in despesas" :key="index">
            <td>{{ item.ano }}</td>
            <td>{{ item.trimestre }}</td>
            <td :class="{'positivo': item.valor_despesas > 0}">
              {{ formatarMoeda(item.valor_despesas) }}
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-else class="sem-dados">
        <p>Nenhum registro de despesa assistencial encontrado para esta operadora.</p>
        <small>Nota: Administradoras de Benefícios geralmente não possuem despesas assistenciais diretas.</small>
      </div>
    </div>
  </div>
  <div v-else class="loading">Carregando dados da operadora...</div>
</template>

<script>
import api from '../services/api';

export default {
  data() {
    return {
      operadora: null,
      despesas: [],
      loading: true
    };
  },
  async mounted() {
    // Pega o CNPJ da URL (ex: /operadora/123456...)
    const cnpj = this.$route.params.cnpj;
    await this.carregarDados(cnpj);
  },
  methods: {
    async carregarDados(cnpj) {
      this.loading = true;
      try {
        // Busca dados cadastrais
        const opResponse = await api.getOperadoraDetalhe(cnpj);
        this.operadora = opResponse.data;

        // Busca histórico financeiro
        const despResponse = await api.getOperadoraDespesas(cnpj);
        this.despesas = despResponse.data;
        
      } catch (error) {
        alert("Erro ao carregar dados da operadora. Verifique se o CNPJ está correto.");
        this.$router.push('/');
      } finally {
        this.loading = false;
      }
    },
    formatarMoeda(valor) {
      if (!valor) return 'R$ 0,00';
      return parseFloat(valor).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }
  }
};
</script>

<style scoped>
.detalhes-container { max-width: 800px; margin: 0 auto; padding: 20px; }
.card-info { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #eee; }
.btn-voltar { background: #2563eb; border: 1px solid #cccccc; padding: 8px 16px; cursor: pointer; margin-bottom: 20px; border-radius: 4px; }
.tabela-despesas { width: 100%; border-collapse: collapse; margin-top: 10px; }
.tabela-despesas th, .tabela-despesas td { border: 1px solid #ddd; padding: 10px; text-align: left; }
.sem-dados { padding: 20px; background: #fff3cd; border: 1px solid #ffeeba; color: #856404; border-radius: 4px; }
</style>