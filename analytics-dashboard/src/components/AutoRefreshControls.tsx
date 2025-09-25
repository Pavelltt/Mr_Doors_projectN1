import { Card, Group, Switch, Text, NumberInput, Stack, Badge, ActionIcon, Tooltip, Alert } from '@mantine/core'
import { IconRefresh, IconPlayerPause, IconPlayerPlay, IconSettings, IconAlertCircle } from '@tabler/icons-react'
import { useState } from 'react'
import useAutoRefresh from '../hooks/useAutoRefresh'

export function AutoRefreshControls() {
  const {
    overviewConfig,
    chartsConfig,
    tableConfig,
    setOverviewRefresh,
    setChartsRefresh,
    setTableRefresh,
    forceRefreshAll,
    pauseAll,
    resumeAll,
    isGloballyPaused,
    clearErrors,
  } = useAutoRefresh()
  
  const [showSettings, setShowSettings] = useState(false)

  const handleIntervalChange = (type: 'overview' | 'charts' | 'table', value: number | string) => {
    if (typeof value === 'number' && value >= 5) {
      const intervalMs = value * 1000
      if (type === 'overview') {
        setOverviewRefresh({ interval: intervalMs })
      } else if (type === 'charts') {
        setChartsRefresh({ interval: intervalMs })
      } else if (type === 'table') {
        setTableRefresh({ interval: intervalMs })
      }
    }
  }

  const isAnyEnabled = overviewConfig.enabled || chartsConfig.enabled || tableConfig.enabled

  const getStatusColor = () => {
    if (!isAnyEnabled) return 'gray'
    if (isGloballyPaused) return 'yellow'
    return 'green'
  }

  const getStatusText = () => {
    if (!isAnyEnabled) return 'Выключено'
    if (isGloballyPaused) return 'Приостановлено'
    return 'Активно'
  }

  const toggleGlobalEnabled = () => {
    const newEnabled = !isAnyEnabled
    setOverviewRefresh({ enabled: newEnabled })
    setChartsRefresh({ enabled: newEnabled })
    setTableRefresh({ enabled: newEnabled })
  }

  const hasErrors = overviewConfig.errorCount > 0 || chartsConfig.errorCount > 0 || tableConfig.errorCount > 0

  const renderErrorInfo = (config: typeof overviewConfig, type: 'overview' | 'charts' | 'table', label: string) => {
    if (config.errorCount === 0) return null
    
    return (
      <Alert 
         icon={<IconAlertCircle size={16} />} 
         color="red" 
         variant="light" 
         withCloseButton
         onClose={() => clearErrors(type)}
         mb="xs"
       >
        <Text size="xs">
          <strong>{label}:</strong> {config.errorCount} ошибок
        </Text>
        {config.lastError && (
          <Text size="xs" c="dimmed" truncate>
            {config.lastError}
          </Text>
        )}
      </Alert>
    )
  }

  return (
    <Card withBorder radius="md" shadow="sm" padding="md">
      <Stack gap="md">
        <Group justify="space-between" align="center">
          <Group gap="sm">
            <Text fw={500} size="sm">Автообновление</Text>
            <Badge color={getStatusColor()} size="sm">
              {getStatusText()}
            </Badge>
            {hasErrors && (
              <Badge color="red" size="sm" variant="light">
                Ошибки
              </Badge>
            )}
          </Group>
          
          <Group gap="xs">
            <Tooltip label="Принудительное обновление">
              <ActionIcon
                variant="light"
                color="blue"
                onClick={forceRefreshAll}
                disabled={!isAnyEnabled}
              >
                <IconRefresh size={16} />
              </ActionIcon>
            </Tooltip>
            
            <Tooltip label={isGloballyPaused ? "Возобновить" : "Приостановить"}>
              <ActionIcon
                variant="light"
                color={isGloballyPaused ? "green" : "yellow"}
                onClick={isGloballyPaused ? resumeAll : pauseAll}
                disabled={!isAnyEnabled}
              >
                {isGloballyPaused ? <IconPlayerPlay size={16} /> : <IconPlayerPause size={16} />}
              </ActionIcon>
            </Tooltip>
            
            <Tooltip label="Настройки">
              <ActionIcon
                variant="light"
                color="gray"
                onClick={() => setShowSettings(!showSettings)}
              >
                <IconSettings size={16} />
              </ActionIcon>
            </Tooltip>
          </Group>
        </Group>

        <Group>
          <Switch
            label="Включить автообновление"
            checked={isAnyEnabled}
            onChange={toggleGlobalEnabled}
            size="sm"
          />
        </Group>

        {/* Отображение ошибок */}
        {hasErrors && (
          <Stack gap="xs">
            {renderErrorInfo(overviewConfig, 'overview', 'Обзор')}
            {renderErrorInfo(chartsConfig, 'charts', 'Графики')}
            {renderErrorInfo(tableConfig, 'table', 'Таблица')}
          </Stack>
        )}

        {showSettings && isAnyEnabled && (
          <Stack gap="sm">
            <Text size="xs" c="dimmed">Интервалы обновления (секунды):</Text>
            
            <Group grow>
              <NumberInput
                label="Обзор"
                value={overviewConfig.interval / 1000}
                onChange={(value) => handleIntervalChange('overview', value)}
                min={5}
                max={300}
                size="xs"
                error={overviewConfig.errorCount > 0}
              />
              
              <NumberInput
                label="Графики"
                value={chartsConfig.interval / 1000}
                onChange={(value) => handleIntervalChange('charts', value)}
                min={5}
                max={300}
                size="xs"
                error={chartsConfig.errorCount > 0}
              />
              
              <NumberInput
                label="Таблица"
                value={tableConfig.interval / 1000}
                onChange={(value) => handleIntervalChange('table', value)}
                min={5}
                max={300}
                size="xs"
                error={tableConfig.errorCount > 0}
              />
            </Group>
          </Stack>
        )}
      </Stack>
    </Card>
  )
}