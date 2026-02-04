<template>
  <div>
    <div class="header-action">
      <h1>Operadoras</h1>
      <div class="search-wrapper">
        <input
          v-model="search"
          @keyup.enter="buscar"
          type="text"
          placeholder="🔍 Buscar por Razão Social ou CNPJ"
          class="search-input"
        />
      </div>
    </div>

    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Registro</th>
            <th>Razão Social</th>
            <th>CNPJ</th>
            <th>Modalidade</th>
            <th>UF</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="op in operadoras" :key="op.registro">
            <td>{{ op.registro }}</td>
            <td style="font-weight: 600;">{{ op.razao_social }}</td>
            <td>{{ op.cnpj }}</td>
            <td><span class="badge">{{ op.modalidade }}</span></td>
            <td>{{ op.uf }}</td>
            <td>
              <router-link :to="`/operadora/${op.cnpj}`" class="btn-link">
                Ver Detalhes
              </router-link>
            </td>
          </tr>
          <tr v-if="operadoras.length === 0">
            <td colspan="6" class="text-center">Nenhuma operadora encontrada.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination-wrapper">
      <Pagination
        :page="page"
        :limit="limit"
        :total="total"
        @change="changePage"
      />
    </div>
  </div>
</template>

<script>
import api from "../services/api";
import Pagination from "../components/Pagination.vue";

export default {
  name: "Operadoras",
  components: { Pagination },
  data() {
    return {
      operadoras: [],
      page: 1,
      limit: 10,
      total: 0,
      search: "",
    };
  },
  methods: {
    async fetchOperadoras() {
      try {
        // Usamos getOperadoras em vez de api.get
        const response = await api.getOperadoras(this.page, this.limit, this.search);
        
        this.operadoras = response.data.data;
        this.total = response.data.total;
      } catch (error) {
        console.error("Erro ao buscar operadoras:", error);
      }
    },
    buscar() {
      this.page = 1;
      this.fetchOperadoras();
    },
    changePage(newPage) {
      this.page = newPage;
      this.fetchOperadoras();
    },
  },
  mounted() {
    this.fetchOperadoras();
  },
};
</script>

<style scoped>
.header-action { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.search-wrapper { width: 300px; }
.badge { background-color: #dbeafe; color: #1e40af; padding: 4px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
.pagination-wrapper { margin-top: 1.5rem; display: flex; justify-content: flex-end; }
.btn-link { color: #2563eb; text-decoration: none; font-weight: 600; font-size: 0.9rem; }
.btn-link:hover { text-decoration: underline; }
</style>