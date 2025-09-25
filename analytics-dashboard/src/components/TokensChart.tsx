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
  Legend,
} from 'recharts'
import { useEffect } from 'react'
import { useAnalytics } from '../hooks/useAnalytics'
import { useTokensChart } from '../hooks/useAnalyticsApi'
import useAutoRefresh from '../hooks/useAutoRefresh'

export function TokensChart() {
  const { filters } = useAnalytics()
  const { data: chartData, isLoading, isError, error, refetch } = useTokensChart(filters)
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
            Токены по времени
          </Text>
          <Text size="sm" c="dimmed">
            Динамика использования входных и выходных токенов
          </Text>
        </div>
      </Group>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorInputTokens" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#228be6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#228be6" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorOutputTokens" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#40c057" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#40c057" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.2} />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            stroke="#adb5bd"
            tickFormatter={(value) => new Date(value).toLocaleDateString('ru-RU', { 
              month: 'short', 
              day: 'numeric' 
            })}
          />
          <YAxis 
            tick={{ fontSize: 12 }} 
            stroke="#adb5bd"
            tickFormatter={(value) => value.toLocaleString('ru-RU')}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1a1b1e', 
              borderRadius: '8px', 
              border: 'none',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
            }}
            labelStyle={{ color: '#ced4da' }}
            labelFormatter={(value) => new Date(value).toLocaleDateString('ru-RU')}
            formatter={(value: number, name: string) => [
              value.toLocaleString('ru-RU'),
              name === 'input_tokens' ? 'Входные токены' : 'Выходные токены'
            ]}
          />
          <Legend 
            formatter={(value) => value === 'input_tokens' ? 'Входные токены' : 'Выходные токены'}
          />
          <Area
            type="monotone"
            dataKey="input_tokens"
            stackId="1"
            stroke="#228be6"
            fillOpacity={1}
            fill="url(#colorInputTokens)"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="output_tokens"
            stackId="1"
            stroke="#40c057"
            fillOpacity={1}
            fill="url(#colorOutputTokens)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  )
}