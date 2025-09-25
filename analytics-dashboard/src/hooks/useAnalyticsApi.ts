import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import dayjs from 'dayjs'

import type { AnalyticsFilters } from '../providers/AnalyticsProvider'

export const API_URL = import.meta.env.VITE_ANALYTICS_API_URL ?? 'http://localhost:8000/api/v1'

async function fetcher<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
  const url = new URL(`${API_URL}${path}`)
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        url.searchParams.append(key, String(value))
      }
    })
  }

  const response = await fetch(url.toString())
  if (!response.ok) {
    const message = await response.text()
    throw new Error(`Request failed with status ${response.status}: ${message}`)
  }

  return response.json() as Promise<T>
}

export interface RequestEvent {
  id: number
  request_id: string
  originated_at: string
  chat_id: string | null
  message_id: number | null
  tile_id: string | null
  model: string
  duration_seconds: number
  input_tokens: number
  output_tokens: number
  cost_usd: number
  status: string
  numbers: string[] | null
  created_at: string
  updated_at: string | null
  error_payload?: unknown
  raw_prompt?: string
  raw_response?: string
}

export interface AggregatedMetrics {
  total_requests: number
  total_cost_usd: number
  total_input_tokens: number
  total_output_tokens: number
  average_latency: number | null
}

export interface RequestEventListResponse {
  items: RequestEvent[]
  total: number
  limit: number
  offset: number
  aggregates: AggregatedMetrics
}

export interface CostChartPoint {
  date: string
  cost: number
}

export interface TokensChartPoint {
  date: string
  input_tokens: number
  output_tokens: number
}

export interface ModelDistributionPoint {
  name: string
  value: number
  [key: string]: string | number
}

export function buildQueryParams(
  filters: AnalyticsFilters,
  extras: Record<string, string | number | undefined> = {},
): Record<string, string | number | undefined> {
  const [start, end] = filters.dateRange
  const trimmedSearch = filters.search.trim()

  return {
    ...extras,
    model: filters.models && filters.models.length > 0 && !filters.models.includes('all') ? filters.models.join(',') : undefined,
    status_filter: filters.status === 'all' ? undefined : filters.status,
    chat_id: trimmedSearch ? trimmedSearch : undefined,
    date_from: start ? start.toISOString() : undefined,
    date_to: end ? end.toISOString() : undefined,
  }
}

export function useAnalyticsRequests(filters: AnalyticsFilters, pagination: { limit: number; offset: number }) {
  const params = useMemo(
    () => buildQueryParams(filters, pagination),
    [filters, pagination],
  )

  return useQuery<RequestEventListResponse>({
    queryKey: ['requests', params],
    queryFn: () => fetcher<RequestEventListResponse>('/requests', params),
    staleTime: 30_000,
  })
}

export function useModelsDistribution(filters: AnalyticsFilters) {
  const params = useMemo(() => buildQueryParams(filters, { limit: 100, offset: 0 }), [filters])

  return useQuery<ModelDistributionPoint[]>({
    queryKey: ['models-distribution', params],
    queryFn: async () => {
      const response = await fetcher<RequestEventListResponse>('/requests', params)
      const grouped = new Map<string, number>()

      response.items.forEach((item) => {
        grouped.set(item.model, (grouped.get(item.model) ?? 0) + 1)
      })

      return Array.from(grouped.entries())
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
    },
    staleTime: 30_000,
  })
}

export function useTokensChart(filters: AnalyticsFilters) {
  const params = useMemo(() => buildQueryParams(filters, { limit: 100, offset: 0 }), [filters])

  return useQuery<TokensChartPoint[]>({
    queryKey: ['tokens-chart', params],
    queryFn: async () => {
      const response = await fetcher<RequestEventListResponse>('/requests', params)
      const grouped = new Map<string, { input_tokens: number; output_tokens: number }>()

      response.items.forEach((item) => {
        const day = item.originated_at.slice(0, 10)
        const existing = grouped.get(day) ?? { input_tokens: 0, output_tokens: 0 }
        grouped.set(day, {
          input_tokens: existing.input_tokens + item.input_tokens,
          output_tokens: existing.output_tokens + item.output_tokens,
        })
      })

      return Array.from(grouped.entries())
        .map(([isoDate, tokens]) => ({
          date: isoDate,
          input_tokens: tokens.input_tokens,
          output_tokens: tokens.output_tokens,
          sortKey: isoDate,
        }))
        .sort((a, b) => (a.sortKey < b.sortKey ? -1 : 1))
        .map(({ date, input_tokens, output_tokens }) => ({ date, input_tokens, output_tokens }))
    },
    staleTime: 30_000,
  })
}

export function useAnalyticsAggregates(filters: AnalyticsFilters) {
  const params = useMemo(() => buildQueryParams(filters, { limit: 1, offset: 0 }), [filters])

  return useQuery<AggregatedMetrics>({
    queryKey: ['aggregates', params],
    queryFn: async () => {
      const data = await fetcher<RequestEventListResponse>('/requests', params)
      return data.aggregates
    },
    staleTime: 30_000,
  })
}

export function useCostChart(filters: AnalyticsFilters) {
  const params = useMemo(() => buildQueryParams(filters, { limit: 100, offset: 0 }), [filters])

  return useQuery<CostChartPoint[]>({
    queryKey: ['cost-chart', params],
    queryFn: async () => {
      const response = await fetcher<RequestEventListResponse>('/requests', params)
      const grouped = new Map<string, number>()

      response.items.forEach((item) => {
        const day = item.originated_at.slice(0, 10)
        grouped.set(day, (grouped.get(day) ?? 0) + item.cost_usd)
      })

      return Array.from(grouped.entries())
        .map(([isoDate, cost]) => ({
          date: dayjs(isoDate).format('DD MMM'),
          cost: Number(cost.toFixed(2)),
          sortKey: isoDate,
        }))
        .sort((a, b) => (a.sortKey < b.sortKey ? -1 : 1))
        .map(({ date, cost }) => ({ date, cost }))
    },
    staleTime: 30_000,
  })
}

