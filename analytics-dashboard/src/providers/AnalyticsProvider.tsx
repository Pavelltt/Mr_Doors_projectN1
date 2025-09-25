import { createContext, useState } from 'react'
import type { ReactNode } from 'react'
import dayjs from 'dayjs'

export interface AnalyticsFilters {
  dateRange: [Date, Date]
  search: string
  models: string[]
  status?: string
}

export type DateRangeValue = [Date | null, Date | null]

export interface AnalyticsContextType {
  filters: AnalyticsFilters
  setFilters: (filters: AnalyticsFilters) => void
  updateFilters: (updates: Partial<AnalyticsFilters>) => void
}

const AnalyticsContext = createContext<AnalyticsContextType | null>(null)

interface AnalyticsProviderProps {
  children: ReactNode
}

function AnalyticsProvider({ children }: AnalyticsProviderProps) {
  const [filters, setFilters] = useState<AnalyticsFilters>({
    dateRange: [dayjs().subtract(30, 'day').toDate(), new Date()],
    search: '',
    models: [],
  })

  const updateFilters = (updates: Partial<AnalyticsFilters>) => {
    setFilters(prev => ({ ...prev, ...updates }))
  }

  const value = {
    filters,
    setFilters,
    updateFilters,
  }

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  )
}

// Экспорт компонента для fast refresh
export default AnalyticsProvider
export { AnalyticsContext }

