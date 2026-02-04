import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Operadoras from '../pages/Operadoras.vue'
import Estatisticas from '../pages/Estatisticas.vue'
import OperadoraDetalhe from '../views/OperadoraDetalhe.vue'

const routes = [
  { 
    path: '/', 
    name: 'Operadoras', 
    component: Operadoras 
  },
  { 
    path: '/estatisticas', 
    name: 'Estatisticas', 
    component: Estatisticas 
  },
  { 
    path: '/operadora/:cnpj', 
    name: 'OperadoraDetalhe', 
    component: OperadoraDetalhe 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router