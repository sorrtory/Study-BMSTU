import Config from '../config'

export const storageModels = [
  'pg-jsonb',
  'pg-normalized',
  'mongo-nested',
  'mongo-normalized',
] as const

export const loadScenarios = ['write-heavy', 'analytics-heavy', 'balanced'] as const
export const sizeProfiles = ['small', 'medium', 'large'] as const

export type StorageModel = typeof storageModels[number]
export type LoadScenario = typeof loadScenarios[number]
export type SizeProfile = typeof sizeProfiles[number]

export interface SeedRequest {
  model: StorageModel
  profile?: SizeProfile
  seed?: number
}

export interface ClearRequest {
  model: StorageModel
}

export interface RunRequest {
  model: StorageModel
  scenario?: LoadScenario
  profile?: SizeProfile
  seed?: number
  run_id?: string
  duration_seconds?: number
  stages?: number[]
  event_batch_size?: number
  telemetry_batch_size?: number
}

export interface GrafanaLinks {
  dashboard: string
  embed: string
}

export interface ExperimentState {
  active: boolean
  error?: string
  finished_at?: string
  grafana?: GrafanaLinks
  model?: StorageModel
  phase: 'idle' | 'clearing' | 'seeding' | 'running' | 'finished' | 'failed'
  request?: RunRequest
  run_id?: string
  started_at?: string
  summary?: RunResponse['summary']
}

export interface RunResponse {
  grafana: GrafanaLinks
  state: ExperimentState
  summary: {
    run_id: string
    model: StorageModel
    scenario: LoadScenario
    started_at: string
    finished_at: string
    stages: unknown[]
    totals: Record<string, unknown>
  }
}

export interface LoadgenOptions {
  defaults: Required<Pick<
    RunRequest,
    'duration_seconds' | 'event_batch_size' | 'profile' | 'scenario' | 'seed' | 'stages' | 'telemetry_batch_size'
  >>
  models: StorageModel[]
  profiles: SizeProfile[]
  scenarios: LoadScenario[]
}

export type LoadgenTarget = 'postgres' | 'mongo'
export type LoadgenServiceHealth = 'up' | 'down'
export type LoadgenServiceMode = 'idle' | 'busy' | 'running'

export interface LoadgenServiceStatus {
  checked_at: string
  details?: string
  health: LoadgenServiceHealth
  mode: LoadgenServiceMode
  target: LoadgenTarget
  title: string
  url: string
}

export interface StandStatus {
  experiment: ExperimentState
  grafana: GrafanaLinks
  services: LoadgenServiceStatus[]
}

async function requestApi<TResponse>(path: string, init?: RequestInit): Promise<TResponse> {
  const response = await fetch(`${Config.VITE_API_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  })
  const data = await response.json().catch(() => ({})) as unknown

  if (!response.ok) {
    const message = data && typeof data === 'object' && 'message' in data
      ? String(data.message)
      : `Сервер вернул статус ${response.status}`
    throw new Error(message)
  }

  return data as TResponse
}

function postApi<TResponse>(path: string, body: unknown): Promise<TResponse> {
  return requestApi<TResponse>(path, {
    body: JSON.stringify(body),
    method: 'POST',
  })
}

export function getLoadgenOptions() {
  return requestApi<LoadgenOptions>('/api/loadgen/options')
}

export function getExperimentStatus() {
  return requestApi<ExperimentState>('/api/loadgen/status')
}

export function getStandStatus() {
  return requestApi<StandStatus>('/api/loadgen/stand')
}

export function clearLoadgenModel(payload: ClearRequest) {
  return postApi<{ model: StorageModel; status: 'ok'; state: ExperimentState }>(
    '/api/loadgen/clear',
    payload,
  )
}

export function seedLoadgenModel(payload: SeedRequest) {
  return postApi<{ model: StorageModel; profile: SizeProfile; seed: number; status: 'ok'; state: ExperimentState }>(
    '/api/loadgen/seed',
    payload,
  )
}

export function prepareLoadgenModel(payload: SeedRequest) {
  return postApi<{ state: ExperimentState }>('/api/loadgen/prepare', payload)
}

export function runLoadgenExperiment(payload: RunRequest) {
  return postApi<RunResponse>('/api/loadgen/run', payload)
}
