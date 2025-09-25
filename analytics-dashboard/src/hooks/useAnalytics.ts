import { useContext } from 'react'
import { AnalyticsContext } from '../providers/AnalyticsProvider'

export function useAnalytics() {
  const context = useContext(AnalyticsContext)
  if (context === null) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider')
  }
  return context
}