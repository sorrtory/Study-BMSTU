<script setup lang="ts">
const navItems = [
  { href: '#stand-controls', title: 'Сценарии' },
  { href: '#experiment-status', title: 'Статус' },
  { href: '#grafana', title: 'Метрики Grafana' },
]
</script>

<template>
  <header class="app-header">
    <div class="app-header__brand">
      <span class="app-header__badge">БД</span>
      <div>
        <p class="app-header__label">Курсовая работа</p>
        <h1 class="app-header__title">Система видеонаблюдения</h1>
      </div>
    </div>

    <nav class="app-header__nav" aria-label="Основные разделы">
      <a
        v-for="item in navItems"
        :key="item.href"
        class="app-header__link"
        :href="item.href"
      >
        {{ item.title }}
      </a>
    </nav>
  </header>
</template>

<style scoped>
.app-header {
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  gap: 24px;
  justify-content: space-between;
  padding: 20px 32px;
}

.app-header__brand {
  align-items: center;
  display: flex;
  gap: 14px;
  min-width: 0;
}

.app-header__badge {
  align-items: center;
  background: var(--color-accent-soft);
  border: 1px solid var(--color-accent-border);
  border-radius: 8px;
  color: var(--color-accent);
  display: inline-flex;
  flex: 0 0 auto;
  font-size: 14px;
  font-weight: 700;
  height: 42px;
  justify-content: center;
  width: 42px;
}

.app-header__label {
  color: var(--color-text-muted);
  font-size: 13px;
  margin: 0 0 2px;
}

.app-header__title {
  color: var(--color-text);
  font-size: 20px;
  line-height: 1.2;
  margin: 0;
}

.app-header__nav {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}

.app-header__link {
  border-radius: 6px;
  color: var(--color-text-muted);
  font-size: 14px;
  padding: 8px 10px;
  text-decoration: none;
}

.app-header__link:hover {
  background: var(--color-surface);
  color: var(--color-text);
}

@media (max-width: 720px) {
  .app-header {
    align-items: flex-start;
    flex-direction: column;
    padding: 18px 20px;
  }

  .app-header__nav {
    justify-content: flex-start;
  }
}
</style>
