<template>
  <div class="pagination">
    <button
      :disabled="page === 1"
      @click="$emit('change', page - 1)"
    >
      ◀ Anterior
    </button>

    <span>Página {{ page }} de {{ totalPages }}</span>

    <button
      :disabled="page === totalPages"
      @click="$emit('change', page + 1)"
    >
      Próxima ▶
    </button>
  </div>
</template>

<script>
export default {
  name: "Pagination",
  props: {
    page: Number,
    limit: Number,
    total: Number,
  },
  computed: {
    totalPages() {
      return Math.ceil(this.total / this.limit);
    },
  },
};
</script>

<style scoped>
.pagination {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 20px;
}

button {
  padding: 6px 12px;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
