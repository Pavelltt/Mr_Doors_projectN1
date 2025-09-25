import { useCallback, useMemo } from 'react'
import { ActionIcon, Group, TextInput, Title, SegmentedControl, Select, Menu, Button } from '@mantine/core'
import type { DatesRangeValue } from '@mantine/dates'
import { DatePickerInput } from '@mantine/dates'
import { IconAdjustments, IconRefresh, IconDownload, IconFileSpreadsheet, IconChartBar } from '@tabler/icons-react'
import { useAnalytics } from '../hooks/useAnalytics'
import { type DateRangeValue } from '../providers/AnalyticsProvider'
import { useAnalyticsRequests, useAnalyticsAggregates } from '../hooks/useAnalyticsApi'
import { exportToCSV, exportAggregatedData } from '../utils/export'
import { AutoRefreshControls } from './AutoRefreshControls'

function normalizeRange(value: DateRangeValue | null | undefined): DateRangeValue {
  if (!value) {
    return [null, null]
  }

  const [start, end] = value
  return [start ? new Date(start) : null, end ? new Date(end) : null]
}

export function DashboardHeader() {
  const { filters, setFilters } = useAnalytics();

  // Получаем данные для экспорта
  const { data: requestsData } = useAnalyticsRequests(filters, { limit: 100, offset: 0 })
  const { data: aggregatesData } = useAnalyticsAggregates(filters)

  const handleDateRangeChange = useCallback(
    (value: DatesRangeValue<string>) => {
      const asDates: DateRangeValue | null = value
        ? [value[0] ? new Date(value[0]) : null, value[1] ? new Date(value[1]) : null]
        : null

      const normalizedRange = normalizeRange(asDates)
      if (normalizedRange[0] && normalizedRange[1]) {
        setFilters({ ...filters, dateRange: [normalizedRange[0], normalizedRange[1]] });
      }
    },
    [filters, setFilters],
  )

  const handleExportRequests = () => {
    if (requestsData?.items) {
      exportToCSV(requestsData.items, 'analytics_requests')
    }
  }

  const handleExportSummary = () => {
    if (aggregatesData) {
      exportAggregatedData(
        aggregatesData.total_requests,
        aggregatesData.total_cost_usd,
        aggregatesData.total_input_tokens,
        aggregatesData.total_output_tokens,
        aggregatesData.average_latency,
        'analytics_summary'
      )
    }
  }

  const currentRange = useMemo(() => normalizeRange(filters.dateRange), [filters.dateRange])

  return (
    <>
      <Group justify="space-between" align="center" px="md" py="sm">
        <div>
          <Title order={3}>Аналитика OpenAI запросов</Title>
          <SegmentedControl
            mt="sm"
            size="xs"
            value={filters.models.includes('all') || filters.models.length === 0 ? 'all' : filters.models[0]}
            onChange={(value) => setFilters({ ...filters, models: value === 'all' ? [] : [value] })}
            data={[
              { value: 'all', label: 'Все модели' },
              { value: 'gpt-4o', label: 'GPT-4o' },
              { value: 'gpt-4o-mini', label: 'GPT-4o mini' },
            ]}
          />
        </div>
        <Group align="center" gap="sm">
        <TextInput
          placeholder="Поиск по chat_id"
          maw={220}
          size="sm"
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />
        <Select
          placeholder="Статус"
          size="sm"
          maw={140}
          value={filters.status}
          onChange={(value) => setFilters({ ...filters, status: value || 'all' })}
          data={[
            { value: 'all', label: 'Все статусы' },
            { value: 'success', label: 'Успешные' },
            { value: 'error', label: 'Ошибки' },
            { value: 'partial', label: 'Частичные' },
          ]}
        />
        <DatePickerInput
          type="range"
          size="sm"
          value={currentRange}
          onChange={handleDateRangeChange}
          valueFormat="DD MMM"
          placeholder="Диапазон дат"
        />
        <ActionIcon variant="light" color="blue" size="lg" radius="md">
          <IconAdjustments size={18} />
        </ActionIcon>
        <ActionIcon variant="light" color="green" size="lg" radius="md">
          <IconRefresh size={18} />
        </ActionIcon>
        <Menu shadow="md" width={200}>
          <Menu.Target>
            <Button variant="light" color="indigo" size="sm" leftSection={<IconDownload size={16} />}>
              Экспорт
            </Button>
          </Menu.Target>
          <Menu.Dropdown>
            <Menu.Item 
              leftSection={<IconFileSpreadsheet size={14} />}
              onClick={handleExportRequests}
            >
              Экспорт запросов (CSV)
            </Menu.Item>
            <Menu.Item 
              leftSection={<IconChartBar size={14} />}
              onClick={handleExportSummary}
            >
              Экспорт сводки (CSV)
            </Menu.Item>
          </Menu.Dropdown>
        </Menu>
      </Group>
    </Group>
    <AutoRefreshControls />
  </>
  )
}

