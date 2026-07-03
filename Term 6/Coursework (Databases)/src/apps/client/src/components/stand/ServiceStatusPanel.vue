<script setup lang="ts">
import { computed } from 'vue'
import type { LoadgenServiceStatus } from '../../api/loadgen'

const props = defineProps<{
  services: LoadgenServiceStatus[]
}>()

const serviceRows = computed(() => props.services.map((service) => ({
  ...service,
  healthText: service.health === 'up' ? 'up' : 'down',
  modeText: modeLabels[service.mode],
})))

const modeLabels: Record<LoadgenServiceStatus['mode'], string> = {
  busy: 'служебная операция',
  idle: 'простаивает',
  running: 'нагрузка',
}
</script>

<template>
  <section class="service-status" aria-label="Состояние loadgen">
    <div class="service-status__header">
      <h3 class="service-status__title">Loadgen сервисы</h3>
      <span class="service-status__count">{{ serviceRows.length }}</span>
    </div>

    <div class="service-status__list">
      <article v-for="service in serviceRows" :key="service.target" class="service-status__row">
        <div class="service-status__main">
          <span :class="['service-status__dot', `service-status__dot--${service.health}`]" aria-hidden="true" />
          <div class="service-status__text">
            <h4 class="service-status__name">{{ service.title }}</h4>
            <p class="service-status__url">{{ service.url }}</p>
          </div>
        </div>
        <div class="service-status__meta">
          <span :class="['service-status__pill', `service-status__pill--${service.health}`]">
            {{ service.healthText }}
          </span>
          <span class="service-status__pill">{{ service.modeText }}</span>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.service-status {
  background: var(--color-panel);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 20px;
}

.service-status__header {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-bottom: 16px;
}

.service-status__title {
  color: var(--color-text);
  font-size: 18px;
  line-height: 1.3;
  margin: 0;
}

.service-status__count,
.service-status__pill {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  color: var(--color-text-muted);
  font-size: 13px;
  padding: 5px 9px;
}

.service-status__list {
  display: grid;
  gap: 12px;
}

.service-status__row {
  align-items: center;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  display: flex;
  gap: 14px;
  justify-content: space-between;
  min-width: 0;
  padding: 13px;
}

.service-status__main,
.service-status__meta {
  align-items: center;
  display: flex;
  gap: 10px;
  min-width: 0;
}

.service-status__dot {
  border-radius: 50%;
  flex: 0 0 auto;
  height: 10px;
  width: 10px;
}

.service-status__dot--up {
  background: #1f9d55;
}

.service-status__dot--down {
  background: #c24135;
}

.service-status__text {
  min-width: 0;
}

.service-status__name {
  color: var(--color-text);
  font-size: 15px;
  margin: 0;
}

.service-status__url {
  color: var(--color-text-muted);
  font-size: 13px;
  margin: 3px 0 0;
  overflow-wrap: anywhere;
}

.service-status__pill--up {
  background: #e8f5ec;
  border-color: #a9d9b6;
  color: #1f7a3b;
}

.service-status__pill--down {
  background: #fff0ef;
  border-color: #f0b5af;
  color: #a83a31;
}

@media (max-width: 620px) {
  .service-status__row,
  .service-status__meta {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
