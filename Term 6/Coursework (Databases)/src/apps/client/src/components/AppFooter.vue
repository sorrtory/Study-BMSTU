<script setup lang="ts">
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="app-footer">
    <p class="app-footer__text">
      BMSTU DB Coursework · {{ currentYear }}
    </p>
    <p class="app-footer__meta">
      PostgreSQL · MongoDB · Vue 3
    </p>
  </footer>
</template>

<style scoped>
.app-footer {
  align-items: center;
  border-top: 1px solid var(--color-border);
  color: var(--color-text-muted);
  display: flex;
  gap: 16px;
  justify-content: space-between;
  padding: 18px 32px;
}

.app-footer__text,
.app-footer__meta {
  font-size: 14px;
  margin: 0;
}

@media (max-width: 640px) {
  .app-footer {
    align-items: flex-start;
    flex-direction: column;
    gap: 6px;
    padding: 18px 20px;
  }
}
</style>
