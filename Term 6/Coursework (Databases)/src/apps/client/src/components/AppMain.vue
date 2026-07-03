<script setup lang="ts">
import ExperimentStatus from './stand/ExperimentStatus.vue'
import GrafanaEmbed from './stand/GrafanaEmbed.vue'
import ServiceStatusPanel from './stand/ServiceStatusPanel.vue'
import StandControls from './stand/StandControls.vue'
import { useStandController } from '../composables/useStandController'

const {
  action,
  clearModel,
  errorMessage,
  experiment,
  grafana,
  isBusy,
  options,
  refreshStand,
  runExperiment,
  services,
  updatedAt,
} = useStandController()
</script>

<template>
  <main class="app-main">
    <section class="app-main__intro">
      <p class="app-main__eyebrow">Стенд нагрузочного тестирования</p>
      <h2 class="app-main__title">
        Управление PostgreSQL и MongoDB loadgen
      </h2>
      <p class="app-main__description">
        Запуск сценариев, подготовка данных, состояние сервисов и живые графики
        Grafana в одном рабочем экране.
      </p>
    </section>

    <section class="app-main__grid" aria-label="Рабочая область стенда">
      <StandControls
        id="stand-controls"
        class="app-main__wide"
        :action="action"
        :busy="isBusy"
        :options="options"
        @clear="clearModel"
        @run="runExperiment"
      />

      <ExperimentStatus
        id="experiment-status"
        :error-message="errorMessage"
        :experiment="experiment"
        :updated-at="updatedAt"
        @refresh="refreshStand"
      />

      <ServiceStatusPanel :services="services" />

      <GrafanaEmbed id="grafana" class="app-main__wide" :grafana="grafana" />
    </section>
  </main>
</template>

<style scoped>
.app-main {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 28px;
  padding: 40px 32px;
}

.app-main__intro {
  max-width: 820px;
}

.app-main__eyebrow {
  color: var(--color-accent);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0;
  margin: 0 0 10px;
  text-transform: uppercase;
}

.app-main__title {
  color: var(--color-text);
  font-size: 34px;
  line-height: 1.15;
  margin: 0;
}

.app-main__description {
  color: var(--color-text-muted);
  font-size: 17px;
  line-height: 1.55;
  margin: 14px 0 0;
  max-width: 700px;
}

.app-main__grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.app-main__wide {
  grid-column: 1 / -1;
}

@media (max-width: 760px) {
  .app-main {
    padding: 32px 20px;
  }

  .app-main__title {
    font-size: 28px;
  }

  .app-main__grid {
    grid-template-columns: 1fr;
  }
}
</style>
