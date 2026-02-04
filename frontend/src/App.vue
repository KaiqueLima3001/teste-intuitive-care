<script setup>
import { RouterView, RouterLink } from 'vue-router'
</script>

<template>
  <div class="app-layout">
    <header class="navbar">
      <div class="container navbar-content">
        <div class="logo">Intuitive Care</div>
        <nav>
          <RouterLink to="/" class="nav-link">Operadoras</RouterLink>
          <RouterLink to="/estatisticas" class="nav-link">Estatísticas</RouterLink>
        </nav>
      </div>
    </header>

    <main class="container">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.navbar {
  background-color: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 0;
  margin-bottom: 2rem;
}

.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-weight: bold;
  font-size: 1.25rem;
  color: #2563eb;
}

.nav-link {
  margin-left: 20px;
  text-decoration: none;
  color: #4b5563;
  font-weight: 500;
}

.nav-link:hover, 
.router-link-active {
  color: #2563eb; 
}
</style>