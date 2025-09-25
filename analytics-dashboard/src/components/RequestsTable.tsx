import { useMemo, useState, useEffect } from 'react'
import dayjs from 'dayjs'
import { useAnalyticsRequests, type RequestEvent } from '../hooks/useAnalyticsApi'
import { useAnalytics } from '../hooks/useAnalytics'
import { Pagination, ActionIcon, Group, Card, Table, Text, Badge, ScrollArea, Loader, Center, Alert } from '@mantine/core'
import { IconEdit, IconTrash, IconAlertCircle, IconEye } from '@tabler/icons-react'
import { ErrorDetailsModal } from './ErrorDetailsModal'
import useAutoRefresh from '../hooks/useAutoRefresh'

export function RequestsTable() {
  const { filters } = useAnalytics()
  const [page, setPage] = useState(1)
  const [selectedRequest, setSelectedRequest] = useState<RequestEvent | null>(null)
  const [modalOpened, setModalOpened] = useState(false)
  const limit = 20
  const pagination = useMemo(() => ({ limit, offset: (page - 1) * limit }), [page])
  const { data, isLoading, isError, error, refetch } = useAnalyticsRequests(filters, pagination)
  const { onTableRefresh, reportError, clearErrors } = useAutoRefresh()

  // Подписка на автообновление
  useEffect(() => {
    const unsubscribe = onTableRefresh(async () => {
      try {
        await refetch()
        clearErrors('table')
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Ошибка при обновлении таблицы'
        reportError('table', errorMessage)
      }
    })
    return unsubscribe
  }, [onTableRefresh, refetch, reportError, clearErrors])

  const statusColors: Record<string, string> = {
    success: 'green',
    error: 'red',
    partial: 'yellow',
  };

  const handleViewDetails = (request: RequestEvent) => {
    setSelectedRequest(request)
    setModalOpened(true)
  }

  if (isLoading) {
    return (
      <Card withBorder radius="md" shadow="sm" padding="lg" style={{ width: '100%' }}>
        <Center style={{ height: 300 }}>
          <Loader size="sm" />
        </Center>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card withBorder radius="md" shadow="sm" padding="lg" style={{ width: '100%' }}>
        <Alert icon={<IconAlertCircle size={16} />} color="red" title="Не удалось загрузить запросы">
          {error instanceof Error ? error.message : 'Попробуйте обновить страницу.'}
        </Alert>
      </Card>
    );
  }

  const rows = data.items.length ? (
    data.items.map((request) => (
      <Table.Tr key={request.request_id}>
        <Table.Td>{request.request_id}</Table.Td>
        <Table.Td>{request.model}</Table.Td>
        <Table.Td>{`${request.duration_seconds.toFixed(1)}s`}</Table.Td>
        <Table.Td>{`${request.input_tokens}/${request.output_tokens}`}</Table.Td>
        <Table.Td>{`$${request.cost_usd.toFixed(4)}`}</Table.Td>
        <Table.Td>
          <Badge color={statusColors[request.status] || 'gray'} variant="light">
            {request.status}
          </Badge>
        </Table.Td>
        <Table.Td>{dayjs(request.originated_at).format('YYYY-MM-DD HH:mm:ss')}</Table.Td>
        <Table.Td>
          <Group>
            <ActionIcon 
              variant="light" 
              color="blue" 
              onClick={() => handleViewDetails(request)}
              title="Просмотр деталей"
            >
              <IconEye size={16} />
            </ActionIcon>
            <ActionIcon variant="light" color="gray" disabled title="Редактировать (недоступно)">
              <IconEdit size={16} />
            </ActionIcon>
            <ActionIcon variant="light" color="red" disabled title="Удалить (недоступно)">
              <IconTrash size={16} />
            </ActionIcon>
          </Group>
        </Table.Td>
      </Table.Tr>
    ))
  ) : (
    <Table.Tr>
      <Table.Td colSpan={8}>
        <Text ta="center" c="dimmed">
          Нет данных для отображения.
        </Text>
      </Table.Td>
    </Table.Tr>
  );

  return (
    <Card withBorder radius="md" shadow="sm" padding="lg" style={{ width: '100%' }}>
      <Group justify="space-between" mb="md">
        <div>
          <Text size="lg" fw={500}>
            Последние запросы
          </Text>
          <Text size="sm" c="dimmed">
            Детальная информация о каждом обращении к модели.
          </Text>
        </div>
      </Group>
      <ScrollArea h={360} type="auto">
        <Table verticalSpacing="sm" striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Request ID</Table.Th>
              <Table.Th>Model</Table.Th>
              <Table.Th>Duration</Table.Th>
              <Table.Th>Tokens</Table.Th>
              <Table.Th>Cost</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Originated</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{rows}</Table.Tbody>
        </Table>
      </ScrollArea>
      <Pagination total={Math.max(1, Math.ceil(data.total / limit))} value={page} onChange={setPage} mt="md" />
      
      <ErrorDetailsModal
        opened={modalOpened}
        onClose={() => setModalOpened(false)}
        request={selectedRequest}
      />
    </Card>
  );
}

