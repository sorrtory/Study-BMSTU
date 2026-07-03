<script setup lang="ts">
import type { GrafanaLinks } from '../../api/loadgen'

defineProps<{
  grafana: GrafanaLinks | null
}>()
</script>

<template>
  <section class="grafana-embed" aria-label="Grafana">
    <div class="grafana-embed__header">
      <h3 class="grafana-embed__title">Grafana</h3>
      <a
        v-if="grafana"
        class="grafana-embed__link"
        :href="grafana.dashboard"
        rel="noreferrer"
        target="_blank"
      >
        Открыть dashboard
      </a>
    </div>

    <iframe
      v-if="grafana"
      class="grafana-embed__frame"
      :src="grafana.embed"
      title="Grafana loadgen dashboard"
    />
    <div v-else class="grafana-embed__empty">
      <p class="grafana-embed__empty-title">Dashboard пока недоступен</p>
      <p class="grafana-embed__empty-text">После первого обновления здесь появятся графики стенда.</p>
    </div>
  </section>
</template>

<style scoped>
.grafana-embed {
  background: var(--color-panel);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 20px;
}

.grafana-embed__header {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 16px;
}

.grafana-embed__title {
  color: var(--color-text);
  font-size: 18px;
  line-height: 1.3;
  margin: 0;
}

.grafana-embed__link {
  color: var(--color-accent);
  font-weight: 700;
  text-decoration: none;
}

.grafana-embed__link:hover {
  text-decoration: underline;
}

.grafana-embed__frame,
.grafana-embed__empty {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  min-height: 520px;
  width: 100%;
}

.grafana-embed__frame {
  display: block;
}

.grafana-embed__empty {
  align-items: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 24px;
  text-align: center;
}

.grafana-embed__empty-title {
  color: var(--color-text);
  font-weight: 700;
  margin: 0 0 8px;
}

.grafana-embed__empty-text {
  color: var(--color-text-muted);
  margin: 0;
}
</style>
