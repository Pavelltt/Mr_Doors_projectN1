import { 
  Stack, 
  Title, 
  Card, 
  Text, 
  Button, 
  Group, 
  Badge, 
  Grid, 
  Alert,
  ActionIcon,
  Tooltip
} from '@mantine/core'
import { 
  IconDatabase, 
  IconRefresh, 
  IconTrash, 
  IconDownload, 
  IconSettings, 
  IconUsers,
  IconShield,
  IconBell,
  IconInfoCircle
} from '@tabler/icons-react'
import { useState } from 'react'

export function ManagementTab() {
  const [isLoading, setIsLoading] = useState(false)

  const handleDatabaseCleanup = async () => {
    setIsLoading(true)
    // Здесь будет логика очистки базы данных
    setTimeout(() => setIsLoading(false), 2000)
  }

  const handleExportData = async () => {
    setIsLoading(true)
    // Здесь будет логика экспорта данных
    setTimeout(() => setIsLoading(false), 2000)
  }

  const handleRefreshCache = async () => {
    setIsLoading(true)
    // Здесь будет логика обновления кэша
    setTimeout(() => setIsLoading(false), 1000)
  }

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="center">
        <Title order={2}>Управление системой</Title>
        <Badge color="green" variant="light">
          Система работает нормально
        </Badge>
      </Group>

      <Alert icon={<IconInfoCircle size="1rem" />} title="Информация" color="blue">
        Здесь вы можете управлять различными аспектами системы аналитики Mr Doors.
        Будьте осторожны при выполнении операций, которые могут повлиять на данные.
      </Alert>

      <Grid>
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>База данных</Text>
              <IconDatabase size="1.2rem" color="var(--mantine-color-blue-6)" />
            </Group>
            <Text size="sm" c="dimmed" mb="md">
              Управление данными и очистка устаревших записей
            </Text>
            <Group gap="xs">
              <Button 
                variant="light" 
                color="orange" 
                leftSection={<IconTrash size="1rem" />}
                loading={isLoading}
                onClick={handleDatabaseCleanup}
              >
                Очистить старые данные
              </Button>
              <Tooltip label="Экспорт всех данных">
                <ActionIcon 
                  variant="light" 
                  color="blue"
                  loading={isLoading}
                  onClick={handleExportData}
                >
                  <IconDownload size="1rem" />
                </ActionIcon>
              </Tooltip>
            </Group>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>Кэш и производительность</Text>
              <IconRefresh size="1.2rem" color="var(--mantine-color-green-6)" />
            </Group>
            <Text size="sm" c="dimmed" mb="md">
              Обновление кэша для улучшения производительности
            </Text>
            <Button 
              variant="light" 
              color="green" 
              leftSection={<IconRefresh size="1rem" />}
              loading={isLoading}
              onClick={handleRefreshCache}
            >
              Обновить кэш
            </Button>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>Пользователи</Text>
              <IconUsers size="1.2rem" color="var(--mantine-color-purple-6)" />
            </Group>
            <Text size="sm" c="dimmed" mb="md">
              Управление пользователями и правами доступа
            </Text>
            <Button 
              variant="light" 
              color="purple" 
              leftSection={<IconShield size="1rem" />}
              disabled
            >
              Управление доступом
            </Button>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>Настройки системы</Text>
              <IconSettings size="1.2rem" color="var(--mantine-color-gray-6)" />
            </Group>
            <Text size="sm" c="dimmed" mb="md">
              Конфигурация системы и уведомлений
            </Text>
            <Group gap="xs">
              <Button 
                variant="light" 
                color="gray" 
                leftSection={<IconSettings size="1rem" />}
                disabled
              >
                Настройки
              </Button>
              <Button 
                variant="light" 
                color="yellow" 
                leftSection={<IconBell size="1rem" />}
                disabled
              >
                Уведомления
              </Button>
            </Group>
          </Card>
        </Grid.Col>
      </Grid>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Title order={4} mb="md">Статистика системы</Title>
        <Grid>
          <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
            <Text size="sm" c="dimmed">Всего запросов</Text>
            <Text size="xl" fw={700}>1,234</Text>
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
            <Text size="sm" c="dimmed">Активных пользователей</Text>
            <Text size="xl" fw={700}>12</Text>
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
            <Text size="sm" c="dimmed">Размер БД</Text>
            <Text size="xl" fw={700}>45.2 MB</Text>
          </Grid.Col>
          <Grid.Col span={{ base: 12, sm: 6, md: 3 }}>
            <Text size="sm" c="dimmed">Время работы</Text>
            <Text size="xl" fw={700}>7д 12ч</Text>
          </Grid.Col>
        </Grid>
      </Card>
    </Stack>
  )
}