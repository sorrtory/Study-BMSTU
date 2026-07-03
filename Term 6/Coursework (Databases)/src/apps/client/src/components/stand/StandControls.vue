<script setup lang="ts">
import { computed, shallowRef } from 'vue'
import {
  loadScenarios,
  sizeProfiles,
  storageModels,
  type LoadgenOptions,
  type LoadScenario,
  type RunRequest,
  type SeedRequest,
  type SizeProfile,
  type StorageModel,
} from '../../api/loadgen'
import type { StandAction } from '../../composables/useStandController'

const props = defineProps<{
  action: StandAction | null
  busy: boolean
  options: LoadgenOptions | null
}>()

const emit = defineEmits<{
  clear: [payload: SeedRequest]
  run: [payload: RunRequest]
}>()

const model = shallowRef<StorageModel>('pg-jsonb')
const scenario = shallowRef<LoadScenario>('balanced')
const profile = shallowRef<SizeProfile>('small')
const durationSeconds = shallowRef(60)
const seed = shallowRef(42)
const stagesText = shallowRef('1, 5, 10, 25')
const eventBatchSize = shallowRef(25)
const telemetryBatchSize = shallowRef(50)

const availableModels = computed(() => props.options?.models ?? [...storageModels])
const availableScenarios = computed(() => props.options?.scenarios ?? [...loadScenarios])
const availableProfiles = computed(() => props.options?.profiles ?? [...sizeProfiles])
const parsedStages = computed(() => stagesText.value
  .split(',')
  .map((stage) => Number(stage.trim()))
  .filter((stage) => Number.isInteger(stage) && stage > 0))

const selectedScenarioTitle = computed(() => scenarioLabels[scenario.value])
const isInvalid = computed(() => parsedStages.value.length === 0 || durationSeconds.value < 1 || seed.value < 1)

const scenarioLabels: Record<LoadScenario, string> = {
  'analytics-heavy': 'Analytics-heavy',
  balanced: 'Balanced',
  'write-heavy': 'Write-heavy',
}

const modelLabels: Record<StorageModel, string> = {
  'mongo-nested': 'MongoDB nested',
  'mongo-normalized': 'MongoDB normalized',
  'pg-jsonb': 'PostgreSQL JSONB',
  'pg-normalized': 'PostgreSQL normalized',
}

const profileLabels: Record<SizeProfile, string> = {
  large: 'large',
  medium: 'medium',
  small: 'small',
}

function seedPayload(): SeedRequest {
  return {
    model: model.value,
    profile: profile.value,
    seed: seed.value,
  }
}

function runPayload(): RunRequest {
  return {
    ...seedPayload(),
    duration_seconds: durationSeconds.value,
    event_batch_size: eventBatchSize.value,
    scenario: scenario.value,
    stages: parsedStages.value,
    telemetry_batch_size: telemetryBatchSize.value,
  }
}
</script>

<template>
  <section class="stand-controls" aria-label="Управление стендом">
    <div class="stand-controls__header">
      <div>
        <h3 class="stand-controls__title">Управление стендом</h3>
        <p class="stand-controls__subtitle">{{ selectedScenarioTitle }}</p>
      </div>
      <span class="stand-controls__badge">{{ busy ? 'занят' : 'готов' }}</span>
    </div>

    <div class="stand-controls__grid">
      <label class="stand-controls__field">
        <span class="stand-controls__label">
          Модель
          <span
            class="stand-controls__help"
            data-tooltip="Выбирает схему хранения, для которой будет очищена база, создан тестовый набор данных и запущена нагрузка."
            tabindex="0"
          >?</span>
        </span>
        <select v-model="model" class="stand-controls__select">
          <option v-for="item in availableModels" :key="item" :value="item">
            {{ modelLabels[item] }}
          </option>
        </select>
      </label>

      <label class="stand-controls__field">
        <span class="stand-controls__label">
          Сценарий
          <span
            class="stand-controls__help"
            data-tooltip="Определяет смесь операций: больше записей, больше аналитических чтений или сбалансированная нагрузка."
            tabindex="0"
          >?</span>
        </span>
        <select v-model="scenario" class="stand-controls__select">
          <option v-for="item in availableScenarios" :key="item" :value="item">
            {{ scenarioLabels[item] }}
          </option>
        </select>
      </label>

      <label class="stand-controls__field">
        <span class="stand-controls__label">
          Профиль
          <span
            class="stand-controls__help"
            data-tooltip="Задает размер синтетической предметной области: количество зон, камер и исходных данных."
            tabindex="0"
          >?</span>
        </span>
        <select v-model="profile" class="stand-controls__select">
          <option v-for="item in availableProfiles" :key="item" :value="item">
            {{ profileLabels[item] }}
          </option>
        </select>
      </label>

      <label class="stand-controls__field">
        <span class="stand-controls__label">
          Seed
          <span
            class="stand-controls__help"
            data-tooltip="Фиксирует генератор данных, чтобы один и тот же запуск можно было воспроизвести."
            tabindex="0"
          >?</span>
        </span>
        <input v-model.number="seed" class="stand-controls__input" min="1" type="number">
      </label>

      <label class="stand-controls__field">
        <span class="stand-controls__label">
          Длительность, с
          <span
            class="stand-controls__help"
            data-tooltip="Сколько секунд длится каждая ступень нагрузки из списка клиентов."
            tabindex="0"
          >?</span>
        </span>
        <input v-model.number="durationSeconds" class="stand-controls__input" min="1" type="number">
      </label>

      <label class="stand-controls__field">
        <span class="stand-controls__label">
          Ступени клиентов
          <span
            class="stand-controls__help"
            data-tooltip="Список параллельных воркеров по этапам. Например, 1, 5, 10, 25 покажет поведение при росте нагрузки."
            tabindex="0"
          >?</span>
        </span>
        <input v-model="stagesText" class="stand-controls__input" type="text">
      </label>

      <label class="stand-controls__field">
        <span class="stand-controls__label">
          Batch событий
          <span
            class="stand-controls__help"
            data-tooltip="Размер пачки при записи сложных событий видеонаблюдения."
            tabindex="0"
          >?</span>
        </span>
        <input v-model.number="eventBatchSize" class="stand-controls__input" min="1" type="number">
      </label>

      <label class="stand-controls__field">
        <span class="stand-controls__label">
          Batch телеметрии
          <span
            class="stand-controls__help"
            data-tooltip="Размер пачки при записи телеметрии камер."
            tabindex="0"
          >?</span>
        </span>
        <input v-model.number="telemetryBatchSize" class="stand-controls__input" min="1" type="number">
      </label>
    </div>

    <div class="stand-controls__actions">
      <button
        class="stand-controls__button stand-controls__button--muted"
        :disabled="busy"
        title="Удаляет данные выбранной модели. Полезно, когда нужно вручную сбросить стенд без запуска теста."
        type="button"
        @click="emit('clear', seedPayload())"
      >
        {{ action === 'clear' ? 'Очистка...' : 'Очистить модель' }}
      </button>
      <button
        class="stand-controls__button"
        :disabled="busy || isInvalid"
        title="Сначала очищает выбранную модель и заполняет ее тестовыми данными, затем запускает нагрузочный сценарий."
        type="button"
        @click="emit('run', runPayload())"
      >
        {{ action === 'run' ? 'Подготовка и запуск...' : 'Подготовить и запустить' }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.stand-controls {
  background: var(--color-panel);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 20px;
}

.stand-controls__header,
.stand-controls__actions {
  align-items: center;
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.stand-controls__title {
  color: var(--color-text);
  font-size: 18px;
  line-height: 1.3;
  margin: 0;
}

.stand-controls__subtitle {
  color: var(--color-text-muted);
  margin: 4px 0 0;
}

.stand-controls__badge {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 999px;
  color: var(--color-text-muted);
  font-size: 13px;
  padding: 5px 9px;
}

.stand-controls__grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 18px;
}

.stand-controls__field {
  display: grid;
  gap: 6px;
}

.stand-controls__label {
  align-items: center;
  color: var(--color-text-muted);
  display: inline-flex;
  font-size: 13px;
  gap: 6px;
  min-width: 0;
}

.stand-controls__help {
  align-items: center;
  background: var(--color-panel);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  color: var(--color-text-muted);
  cursor: help;
  display: inline-flex;
  flex: 0 0 auto;
  font-size: 11px;
  font-weight: 700;
  height: 18px;
  justify-content: center;
  position: relative;
  width: 18px;
}

.stand-controls__help::after {
  background: #172033;
  border-radius: 6px;
  bottom: calc(100% + 8px);
  color: #ffffff;
  content: attr(data-tooltip);
  font-size: 12px;
  font-weight: 500;
  left: 50%;
  line-height: 1.35;
  opacity: 0;
  padding: 8px 10px;
  pointer-events: none;
  position: absolute;
  transform: translateX(-50%);
  transition: opacity 0.12s ease;
  visibility: hidden;
  width: min(280px, 78vw);
  z-index: 10;
}

.stand-controls__help:hover::after,
.stand-controls__help:focus::after {
  opacity: 1;
  visibility: visible;
}

.stand-controls__input,
.stand-controls__select {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  color: var(--color-text);
  min-width: 0;
  padding: 10px 11px;
  width: 100%;
}

.stand-controls__actions {
  justify-content: flex-end;
  margin-top: 18px;
}

.stand-controls__button {
  background: var(--color-accent);
  border: 1px solid var(--color-accent);
  border-radius: 6px;
  color: #ffffff;
  cursor: pointer;
  font-weight: 700;
  padding: 11px 14px;
}

.stand-controls__button--muted {
  background: var(--color-surface);
  border-color: var(--color-border);
  color: var(--color-text);
}

.stand-controls__button:disabled {
  cursor: progress;
  opacity: 0.62;
}

@media (max-width: 900px) {
  .stand-controls__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .stand-controls__header,
  .stand-controls__actions {
    align-items: stretch;
    flex-direction: column;
  }

  .stand-controls__grid {
    grid-template-columns: 1fr;
  }

  .stand-controls__button {
    width: 100%;
  }
}
</style>
