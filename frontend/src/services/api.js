import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
});

// Exporta as funções que as páginas vão usar
export default {
  getOperadoras(page = 1, limit = 10, search = '') {
    // passando search como parâmetro
    return api.get(`/operadoras/?page=${page}&limit=${limit}&search=${search}`);
  },
  getOperadoraDetalhe(cnpj) {
    return api.get(`/operadoras/${cnpj}`);
  },
  getOperadoraDespesas(cnpj) {
    return api.get(`/operadoras/${cnpj}/despesas`);
  },
  getEstatisticas() {
    return api.get('/estatisticas/');
  }
};