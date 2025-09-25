import { Card, Group, Stack, Text, ThemeIcon, Loader, Center, Alert } from '@mantine/core'
import {
  IconActivity,
  IconCashBanknote,
  IconCoin,
  IconGauge,
  IconAlertCircle,
} from '@tabler/icons-react'
import { useEffect } from 'react'
import { useAnalyticsAggregates } from '../hooks/useAnalyticsApi'
import { useAnalytics } from '../hooks/useAnalytics'
import useAutoRefresh from '../hooks/useAutoRefresh'

export function OverviewCards() {
  const { filters } = useAnalytics()
  const { data: aggregates, isLoading, isError, error, refetch } = useAnalyticsAggregates(filters)
  const { onOverviewRefresh, reportError, clearErrors } = useAutoRefresh()

  // Отладочные логи
  console.log('OverviewCards render:', { 
    filters, 
    aggregates, 
    isLoading, 
    isError, 
    error: error?.message 
  })

  // Подписка на автообновление
  useEffect(() => {
    const unsubscribe = onOverviewRefresh(async () => {
      try {
        await refetch()
        clearErrors('overview')
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Ошибка при обновлении данных'
        reportError('overview', errorMessage)
      }
    })
    return unsubscribe
  }, [onOverviewRefresh, refetch, reportError, clearErrors])

  if (isLoading) {
    return (
      <Center style={{ width: '100%' }}>
        <Loader size="sm" />
      </Center>
    )
  }

  if (isError || !aggregates) {
    return (
      <Alert icon={<IconAlertCircle size={16} />} color="red" title="Не удалось загрузить статистику">
        {error instanceof Error ? error.message : 'Попробуйте обновить страницу или проверьте соединение.'}
      </Alert>
    )
  }

  const stats = [
    {
      label: 'Всего запросов',
      value: aggregates.total_requests.toLocaleString('ru-RU'),
      change: '',
      icon: IconActivity,
      color: 'blue',
    },
    {
      label: 'Стоимость',
      value: `$${aggregates.total_cost_usd.toFixed(2)}`,
      change: '',
      icon: IconCashBanknote,
      color: 'green',
    },
    {
      label: 'Входные токены',
      value: aggregates.total_input_tokens.toLocaleString('ru-RU'),
      change: '',
      icon: IconCoin,
      color: 'violet',
    },
    {
      label: 'Средняя задержка',
      value: aggregates.average_latency ? `${aggregates.average_latency.toFixed(1)}s` : '—',
      change: '',
      icon: IconGauge,
      color: 'orange',
    },
  ]

  return (
    <Group grow align="stretch" gap="md">
      {stats.map((stat) => (
        <Card key={stat.label} withBorder radius="md" shadow="sm" padding="lg" style={{ minHeight: '120px' }}>
          <Group align="center" gap="md" wrap="nowrap">
            <ThemeIcon size={46} radius="md" variant="light" color={stat.color}>
              <stat.icon size={24} />
            </ThemeIcon>
            <Stack gap={4} style={{ flex: 1 }}>
              <Text size="xs" c="dimmed" tt="uppercase" fw={500}>
                {stat.label}
              </Text>
              <Text size="xl" fw={700} lh={1.2}>
                {stat.value}
              </Text>
              {stat.change && (
                <Text size="sm" c="dimmed">
                  {stat.change}
                </Text>
              )}
            </Stack>
          </Group>
        </Card>
      ))}
    </Group>
  )
}

