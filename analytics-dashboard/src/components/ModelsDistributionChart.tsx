import { Card, Text, Loader, Center, Alert, Group } from '@mantine/core'
import { IconAlertCircle } from '@tabler/icons-react'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts'
import { useEffect } from 'react'
import { useAnalytics } from '../hooks/useAnalytics'
import { useModelsDistribution } from '../hooks/useAnalyticsApi'
import useAutoRefresh from '../hooks/useAutoRefresh'

const COLORS = [
  '#228be6', // blue
  '#40c057', // green
  '#fd7e14', // orange
  '#e03131', // red
  '#7c2d12', // brown
  '#9775fa', // violet
  '#f783ac', // pink
  '#15aabf', // cyan
]

export function ModelsDistributionChart() {
  const { filters } = useAnalytics()
  const { data: chartData, isLoading, isError, error, refetch } = useModelsDistribution(filters)
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
            Распределение по моделям
          </Text>
          <Text size="sm" c="dimmed">
            Количество запросов к различным моделям ИИ
          </Text>
        </div>
      </Group>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={(props) => {
              const { name, percent } = props as unknown as { name: string; percent: number }
              return `${name} ${(percent * 100).toFixed(0)}%`
            }}
            outerRadius={120}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value: number) => [value.toLocaleString('ru-RU'), 'Запросов']}
            contentStyle={{ 
              backgroundColor: '#1a1b1e', 
              borderRadius: '8px', 
              border: 'none',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
            }}
            labelStyle={{ color: '#ced4da' }}
          />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            formatter={(value) => <span style={{ color: '#ced4da' }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}