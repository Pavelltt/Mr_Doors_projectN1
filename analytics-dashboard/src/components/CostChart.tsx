import { Card, Text, Loader, Center, Alert, Group } from '@mantine/core'
import { IconAlertCircle } from '@tabler/icons-react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useEffect } from 'react'
import { useAnalytics } from '../hooks/useAnalytics'
import { useCostChart } from '../hooks/useAnalyticsApi'
import useAutoRefresh from '../hooks/useAutoRefresh'

export function CostChart() {
  const { filters } = useAnalytics()
  const { data: chartData, isLoading, isError, error, refetch } = useCostChart(filters)
  const { onChartsRefresh, reportError, clearErrors } = useAutoRefresh()
  
  // Подписка на автообновление
  useEffect(() => {
    const unsubscribe = onChartsRefresh(async () => {
      try {
        await refetch()
        clearErrors('charts')
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Ошибка при обновлении графика'
        reportError('charts', errorMessage)
      }
    })
    
    return unsubscribe
  }, [onChartsRefresh, refetch, reportError, clearErrors])

  if (isLoading) {
    return (
      <Card withBorder radius="md" shadow="sm" padding="lg" style={{ height: 320, width: '100%' }}>
        <Center style={{ height: '100%' }}>
          <Loader size="sm" />
        </Center>
      </Card>
    )
  }

  if (isError || !chartData) {
    return (
      <Card withBorder radius="md" shadow="sm" padding="lg" style={{ height: 320, width: '100%' }}>
        <Center style={{ height: '100%' }}>
          <Alert icon={<IconAlertCircle size={16} />} color="red" title="Не удалось загрузить график">
            {error instanceof Error ? error.message : 'Попробуйте обновить страницу.'}
          </Alert>
        </Center>
      </Card>
    )
  }

  return (
    <Card withBorder radius="md" shadow="sm" padding="lg" style={{ height: '400px' }}>
      <Group justify="space-between" mb="md">
        <div>
          <Text size="lg" fw={500}>
            Стоимость по времени
          </Text>
          <Text size="sm" c="dimmed">
            Динамика затрат на использование API
          </Text>
        </div>
      </Group>
      <ResponsiveContainer width="100%" height="100%">
         <AreaChart data={chartData}>
           <defs>
             <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
               <stop offset="5%" stopColor="#4dabf7" stopOpacity={0.8}/>
               <stop offset="95%" stopColor="#4dabf7" stopOpacity={0}/>
             </linearGradient>
           </defs>
           <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.2} />
           <XAxis 
             dataKey="date" 
             stroke="#adb5bd" 
             tick={{ fontSize: 12 }}
             tickFormatter={(value) => new Date(value).toLocaleDateString('ru-RU', { 
               month: 'short', 
               day: 'numeric' 
             })}
           />
           <YAxis 
             stroke="#adb5bd" 
             tick={{ fontSize: 12 }}
             tickFormatter={(value) => `$${value.toFixed(2)}`}
           />
           <Tooltip
             contentStyle={{ 
               backgroundColor: '#1a1b1e', 
               borderRadius: '8px', 
               border: 'none',
               boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
             }}
             labelStyle={{ color: '#ced4da' }}
             formatter={(value: number) => [`$${value.toFixed(4)}`, 'Стоимость']}
             labelFormatter={(value) => new Date(value).toLocaleDateString('ru-RU')}
           />
           <Area type="monotone" dataKey="cost" stroke="#4dabf7" fill="url(#colorCost)" strokeWidth={2} />
         </AreaChart>
       </ResponsiveContainer>
    </Card>
  )
}

