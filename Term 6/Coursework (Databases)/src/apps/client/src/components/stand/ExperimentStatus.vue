<script setup lang="ts">
import { computed } from 'vue'
import type { ExperimentState } from '../../api/loadgen'

const props = defineProps<{
  errorMessage: string
  experiment: ExperimentState | null
  updatedAt: string
}>()

const emit = defineEmits<{
  refresh: []
}>()

const phaseText = computed(() => {
  switch (props.experiment?.phase) {
    case 'clearing':
      return 'очистка'
    case 'failed':
      return 'ошибка'
    case 'finished':
      return 'завершено'
    case 'running':
      return 'идет тест'
    case 'seeding':
      return 'заполнение'
    case 'idle':
    default:
      return 'простой'
  }
})

const title = computed(() => props.experiment?.active ? 'Стенд занят' : 'Стенд свободен')
const details = computed(() => {
  if (!props.experiment) {
    return 'Ожидание первого снимка состояния'
  }

  if (props.experiment.request) {
    const request = props.experiment.request
    const stages = request.stages?.join(', ') ?? 'ступени по умолчанию'
    const duration = request.duration_seconds ?? 'по умолчанию'

    return `${request.scenario ?? 'balanced'}, ${duration} с, ${stages} клиентов`
  }

  if (props.experiment.error) {
    return props.experiment.error
  }

  return props.experiment.model ?? 'активного теста нет'
})

function formatDate(value?: string) {
  if (!value) {
    return 'нет данных'
  }

  return new Intl.DateTimeFormat('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(new Date(value))
}
</script>

<template>
  <section class="experiment-status" aria-label="Статус эксперимента">
    <div class="experiment-status__header">
      <div>
        <h3 class="experiment-status__title">{{ title }}</h3>
        <p class="experiment-status__subtitle">{{ details }}</p>
      </div>
      <button class="experiment-status__refresh" type="button" @click="emit('refresh')">
        Обновить
      </button>
    </div>

    <dl class="experiment-status__grid">
      <div class="experiment-status__item">
        <dt class="experiment-status__label">Фаза</dt>
        <dd :class="['experiment-status__value', `experiment-status__value--${experiment?.phase ?? 'idle'}`]">
          {{ phaseText }}
        </dd>
      </div>
      <div class="experiment-status__item">
        <dt class="experiment-status__label">Модель</dt>
        <dd class="experiment-status__value">{{ experiment?.model ?? 'не выбрана' }}</dd>
      </div>
      <div class="experiment-status__item">
        <dt class="experiment-status__label">Run ID</dt>
        <dd class="experiment-status__value experiment-status__value--mono">
          {{ experiment?.run_id ?? 'нет' }}
        </dd>
      </div>
      <div class="experiment-status__item">
        <dt class="experiment-status__label">Обновлено</dt>
        <dd class="experiment-status__value">{{ formatDate(updatedAt) }}</dd>
      </div>
    </dl>

    <p v-if="errorMessage || experiment?.error" class="experiment-status__error">
      {{ errorMessage || experiment?.error }}
    </p>
  </section>
</template>

<style scoped>
.experiment-status {
  background: var(--color-panel);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 20px;
}

.experiment-status__header {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.experiment-status__title {
  color: var(--color-text);
  font-size: 18px;
  line-height: 1.3;
  margin: 0;
}

.experiment-status__subtitle {
  color: var(--color-text-muted);
  margin: 4px 0 0;
}

.experiment-status__refresh {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  color: var(--color-text);
  cursor: pointer;
  font-weight: 700;
  padding: 9px 12px;
}

.experiment-status__grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: 18px 0 0;
}

.experiment-status__item {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  min-width: 0;
  padding: 12px;
}

.experiment-status__label {
  color: var(--color-text-muted);
  font-size: 13px;
  margin: 0 0 6px;
}

.experiment-status__value {
  color: var(--color-text);
  font-weight: 700;
  margin: 0;
  overflow-wrap: anywhere;
}

.experiment-status__value--mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 13px;
}

.experiment-status__value--running,
.experiment-status__value--seeding,
.experiment-status__value--clearing {
  color: var(--color-accent);
}

.experiment-status__value--failed {
  color: #a83a31;
}

.experiment-status__error {
  background: #fff0ef;
  border: 1px solid #f0b5af;
  border-radius: 6px;
  color: #a83a31;
  margin: 14px 0 0;
  padding: 10px 12px;
}

@media (max-width: 900px) {
  .experiment-status__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .experiment-status__header {
    align-items: stretch;
    flex-direction: column;
  }

  .experiment-status__grid {
    grid-template-columns: 1fr;
  }
}
</style>
