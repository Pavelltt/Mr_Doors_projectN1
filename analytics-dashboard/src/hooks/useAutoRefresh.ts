import { useContext } from 'react'
import { AutoRefreshContext } from '../providers/AutoRefreshProvider'

export function useAutoRefresh() {
  const context = useContext(AutoRefreshContext)
  if (context === undefined) {
    throw new Error('useAutoRefresh must be used within an AutoRefreshProvider')
  }
  return context
}

export default useAutoRefresh