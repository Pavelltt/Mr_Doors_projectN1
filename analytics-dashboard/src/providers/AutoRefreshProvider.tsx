import { createContext, useState, useEffect, useCallback } from 'react'
import type { ReactNode } from 'react'

export interface RefreshConfig {
  enabled: boolean
  interval: number // в миллисекундах
  lastRefresh: Date | null
  errorCount: number // количество последовательных ошибок
  lastError: string | null // последняя ошибка
}

export interface AutoRefreshContextType {
  // Конфигурации для каждого типа обновления
  overviewConfig: RefreshConfig
  chartsConfig: RefreshConfig
  tableConfig: RefreshConfig

  // Методы для обновления конфигураций
  setOverviewRefresh: (config: Partial<RefreshConfig>) => void
  setChartsRefresh: (config: Partial<RefreshConfig>) => void
  setTableRefresh: (config: Partial<RefreshConfig>) => void

  // Принудительное обновление
  forceRefreshOverview: () => void
  forceRefreshCharts: () => void
  forceRefreshTable: () => void
  forceRefreshAll: () => void

  // Глобальное управление
  pauseAll: () => void
  resumeAll: () => void
  isGloballyPaused: boolean

  // Подписка на события обновления
  onOverviewRefresh: (callback: () => Promise<void> | void) => () => void
  onChartsRefresh: (callback: () => Promise<void> | void) => () => void
  onTableRefresh: (callback: () => Promise<void> | void) => () => void

  // Управление ошибками
  reportError: (type: 'overview' | 'charts' | 'table', error: string) => void
  clearErrors: (type: 'overview' | 'charts' | 'table') => void
}

const AutoRefreshContext = createContext<AutoRefreshContextType | undefined>(undefined)

// Оптимальные интервалы обновления (в миллисекундах)
const DEFAULT_INTERVALS = {
  overview: 30000,    // 30 секунд - общая статистика
  charts: 60000,      // 1 минута - графики
  table: 45000,       // 45 секунд - таблица запросов
}

interface AutoRefreshProviderProps {
  children: ReactNode
}

function AutoRefreshProvider({ children }: AutoRefreshProviderProps) {
  // Состояния конфигураций
  const [overviewConfig, setOverviewConfigState] = useState<RefreshConfig>({
    enabled: true,
    interval: DEFAULT_INTERVALS.overview,
    lastRefresh: null,
    errorCount: 0,
    lastError: null,
  })
  
  const [chartsConfig, setChartsConfigState] = useState<RefreshConfig>({
    enabled: true,
    interval: DEFAULT_INTERVALS.charts,
    lastRefresh: null,
    errorCount: 0,
    lastError: null,
  })
  
  const [tableConfig, setTableConfigState] = useState<RefreshConfig>({
    enabled: true,
    interval: DEFAULT_INTERVALS.table,
    lastRefresh: null,
    errorCount: 0,
    lastError: null,
  })
  
  const [isGloballyPaused, setIsGloballyPaused] = useState(false)
  
  // Колбэки для подписчиков
  const [overviewCallbacks, setOverviewCallbacks] = useState<Set<() => void>>(new Set())
  const [chartsCallbacks, setChartsCallbacks] = useState<Set<() => void>>(new Set())
  const [tableCallbacks, setTableCallbacks] = useState<Set<() => void>>(new Set())
  
  // Методы обновления конфигураций
  const setOverviewRefresh = useCallback((config: Partial<RefreshConfig>) => {
    setOverviewConfigState(prev => ({ ...prev, ...config }))
  }, [])
  
  const setChartsRefresh = useCallback((config: Partial<RefreshConfig>) => {
    setChartsConfigState(prev => ({ ...prev, ...config }))
  }, [])
  
  const setTableRefresh = useCallback((config: Partial<RefreshConfig>) => {
    setTableConfigState(prev => ({ ...prev, ...config }))
  }, [])
  
  // Методы принудительного обновления
  const forceRefreshOverview = useCallback(() => {
    overviewCallbacks.forEach(callback => callback())
    setOverviewConfigState(prev => ({ ...prev, lastRefresh: new Date() }))
  }, [overviewCallbacks])
  
  const forceRefreshCharts = useCallback(() => {
    chartsCallbacks.forEach(callback => callback())
    setChartsConfigState(prev => ({ ...prev, lastRefresh: new Date() }))
  }, [chartsCallbacks])
  
  const forceRefreshTable = useCallback(() => {
    tableCallbacks.forEach(callback => callback())
    setTableConfigState(prev => ({ ...prev, lastRefresh: new Date() }))
  }, [tableCallbacks])
  
  const forceRefreshAll = useCallback(() => {
    forceRefreshOverview()
    forceRefreshCharts()
    forceRefreshTable()
  }, [forceRefreshOverview, forceRefreshCharts, forceRefreshTable])
  
  // Глобальное управление
  const pauseAll = useCallback(() => {
    setIsGloballyPaused(true)
  }, [])
  
  const resumeAll = useCallback(() => {
    setIsGloballyPaused(false)
  }, [])
  
  // Методы подписки на обновления
  const onOverviewRefresh = useCallback((callback: () => void) => {
    setOverviewCallbacks(prev => new Set(prev).add(callback))
    return () => {
      setOverviewCallbacks(prev => {
        const newSet = new Set(prev)
        newSet.delete(callback)
        return newSet
      })
    }
  }, [])
  
  const onChartsRefresh = useCallback((callback: () => void) => {
    setChartsCallbacks(prev => new Set(prev).add(callback))
    return () => {
      setChartsCallbacks(prev => {
        const newSet = new Set(prev)
        newSet.delete(callback)
        return newSet
      })
    }
  }, [])
  
  const onTableRefresh = useCallback((callback: () => void) => {
    setTableCallbacks(prev => new Set(prev).add(callback))
    return () => {
      setTableCallbacks(prev => {
        const newSet = new Set(prev)
        newSet.delete(callback)
        return newSet
      })
    }
  }, [])
  
  // Автоматическое обновление для overview
  useEffect(() => {
    if (!overviewConfig.enabled || isGloballyPaused) return
    
    const interval = setInterval(() => {
      forceRefreshOverview()
    }, overviewConfig.interval)
    
    return () => clearInterval(interval)
  }, [overviewConfig.enabled, overviewConfig.interval, isGloballyPaused, forceRefreshOverview])
  
  // Автоматическое обновление для charts
  useEffect(() => {
    if (!chartsConfig.enabled || isGloballyPaused) return
    
    const interval = setInterval(() => {
      forceRefreshCharts()
    }, chartsConfig.interval)
    
    return () => clearInterval(interval)
  }, [chartsConfig.enabled, chartsConfig.interval, isGloballyPaused, forceRefreshCharts])
  
  // Автоматическое обновление для table
  useEffect(() => {
    if (!tableConfig.enabled || isGloballyPaused) return
    
    const interval = setInterval(() => {
      forceRefreshTable()
    }, tableConfig.interval)
    
    return () => clearInterval(interval)
  }, [tableConfig.enabled, tableConfig.interval, isGloballyPaused, forceRefreshTable])
  
  // Методы для работы с ошибками
  const reportError = useCallback((type: 'overview' | 'charts' | 'table', error: string) => {
    const updateConfig = (config: RefreshConfig): RefreshConfig => ({
      ...config,
      errorCount: config.errorCount + 1,
      lastError: error,
    })
    
    switch (type) {
      case 'overview':
        setOverviewConfigState(updateConfig)
        break
      case 'charts':
        setChartsConfigState(updateConfig)
        break
      case 'table':
        setTableConfigState(updateConfig)
        break
    }
  }, [])
  
  const clearErrors = useCallback((type: 'overview' | 'charts' | 'table') => {
    const clearConfig = (config: RefreshConfig): RefreshConfig => ({
      ...config,
      errorCount: 0,
      lastError: null,
    })
    
    switch (type) {
      case 'overview':
        setOverviewConfigState(clearConfig)
        break
      case 'charts':
        setChartsConfigState(clearConfig)
        break
      case 'table':
        setTableConfigState(clearConfig)
        break
    }
  }, [])

  const value: AutoRefreshContextType = {
    overviewConfig,
    chartsConfig,
    tableConfig,
    setOverviewRefresh,
    setChartsRefresh,
    setTableRefresh,
    forceRefreshOverview,
    forceRefreshCharts,
    forceRefreshTable,
    forceRefreshAll,
    pauseAll,
    resumeAll,
    isGloballyPaused,
    onOverviewRefresh,
    onChartsRefresh,
    onTableRefresh,
    reportError,
    clearErrors,
  }
  
  return (
    <AutoRefreshContext.Provider value={value}>
      {children}
    </AutoRefreshContext.Provider>
  )
}

// Экспорт компонента для fast refresh
export default AutoRefreshProvider
export { AutoRefreshContext }