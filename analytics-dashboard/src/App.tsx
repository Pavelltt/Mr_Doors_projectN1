import { AppShell, Group, Title, Text, Button, TextInput, Stack, Tabs } from '@mantine/core'
import { DashboardHeader } from './components/DashboardHeader'
import { OverviewCards } from './components/OverviewCards'
import { RequestsTable } from './components/RequestsTable'
import { CostChart } from './components/CostChart'
import { TokensChart } from './components/TokensChart'
import { ModelsDistributionChart } from './components/ModelsDistributionChart'
import { ManagementTab } from './components/ManagementTab'
import AnalyticsProvider from './providers/AnalyticsProvider'
import AutoRefreshProvider from './providers/AutoRefreshProvider'
import { useState } from 'react';

const adminPassword = import.meta.env.VITE_ADMIN_PASSWORD ?? 'admin123'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('analytics')

  const handleLogin = () => {
    if (password === adminPassword) {
      setIsAuthenticated(true)
      console.log('Login successful, isAuthenticated set to true')
    } else {
      setError('Неверный пароль')
      console.log('Login failed, incorrect password')
    }
  }

  console.log('App render:', { isAuthenticated, password, error })

  if (!isAuthenticated) {
    return (
      <Stack align="center" justify="center" h="100vh" gap="sm">
        <Title order={3}>Админ-панель Mr Doors</Title>
        <TextInput
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Введите пароль"
          maw={260}
        />
        {error && (
          <Text size="sm" c="red">
            {error}
          </Text>
        )}
        <Button onClick={handleLogin} fullWidth maw={260}>
          Войти
        </Button>
      </Stack>
    )
  }

  return (
    <AnalyticsProvider>
      <AutoRefreshProvider>
        <AppShell
          padding="md"
          header={{ height: 70 }}
        >
          <AppShell.Header>
            <Group justify="space-between" align="center" style={{ height: '100%', padding: '0 16px' }}>
              <Title order={3}>Админ-панель Mr Doors</Title>
              <Button variant="subtle" color="red" onClick={() => setIsAuthenticated(false)}>
                Выйти
              </Button>
            </Group>
          </AppShell.Header>
          <AppShell.Main>
            <Tabs value={activeTab} onChange={(value) => setActiveTab(value || 'analytics')}>
              <Tabs.List>
                <Tabs.Tab value="analytics">Аналитика</Tabs.Tab>
                <Tabs.Tab value="management">Управление</Tabs.Tab>
              </Tabs.List>

              <Tabs.Panel value="analytics" pt="md">
                <Stack gap="lg">
                  <DashboardHeader />
                  <OverviewCards />
                  
                  <Group gap="lg" grow>
                    <CostChart />
                    <TokensChart />
                  </Group>
                  
                  <Group gap="lg" grow>
                    <ModelsDistributionChart />
                  </Group>
                  
                  <RequestsTable />
                </Stack>
              </Tabs.Panel>

              <Tabs.Panel value="management" pt="md">
                <ManagementTab />
              </Tabs.Panel>
            </Tabs>
          </AppShell.Main>
        </AppShell>
      </AutoRefreshProvider>
    </AnalyticsProvider>
  )
}

export default App
