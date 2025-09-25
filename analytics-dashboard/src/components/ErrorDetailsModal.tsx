import { Modal, Text, Stack, Code, ScrollArea, Badge, Group, Divider } from '@mantine/core'
import { IconAlertTriangle, IconClock, IconHash, IconUser } from '@tabler/icons-react'
import dayjs from 'dayjs'
import type { RequestEvent } from '../hooks/useAnalyticsApi'

interface ErrorDetailsModalProps {
  opened: boolean
  onClose: () => void
  request: RequestEvent | null
}

export function ErrorDetailsModal({ opened, onClose, request }: ErrorDetailsModalProps) {
  if (!request) return null

  const hasError = request.status === 'error' && request.error_payload
  const hasNumbers = request.numbers && request.numbers.length > 0

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={
        <Group gap="xs">
          <IconAlertTriangle size={20} color="red" />
          <Text fw={600}>Детали запроса {request.request_id}</Text>
        </Group>
      }
      size="lg"
      scrollAreaComponent={ScrollArea.Autosize}
    >
      <Stack gap="md">
        {/* Основная информация */}
        <Stack gap="xs">
          <Text size="sm" fw={500}>Основная информация</Text>
          <Group gap="md">
            <Group gap="xs">
              <IconHash size={16} />
              <Text size="sm">ID: {request.request_id}</Text>
            </Group>
            <Group gap="xs">
              <IconClock size={16} />
              <Text size="sm">
                {dayjs(request.originated_at).format('DD.MM.YYYY HH:mm:ss')}
              </Text>
            </Group>
            {request.chat_id && (
              <Group gap="xs">
                <IconUser size={16} />
                <Text size="sm">Chat: {request.chat_id}</Text>
              </Group>
            )}
          </Group>
          
          <Group gap="md">
            <Badge color={request.status === 'success' ? 'green' : request.status === 'error' ? 'red' : 'yellow'}>
              {request.status}
            </Badge>
            <Text size="sm">Модель: {request.model}</Text>
            <Text size="sm">Длительность: {request.duration_seconds.toFixed(2)}s</Text>
          </Group>
          
          <Group gap="md">
            <Text size="sm">Токены: {request.input_tokens}/{request.output_tokens}</Text>
            <Text size="sm">Стоимость: ${request.cost_usd.toFixed(4)}</Text>
          </Group>
        </Stack>

        <Divider />

        {/* Извлеченные числа */}
        {hasNumbers && (
          <>
            <Stack gap="xs">
              <Text size="sm" fw={500}>Извлеченные числа</Text>
              <Group gap="xs">
                {request.numbers!.map((number, index) => (
                  <Badge key={index} variant="light" color="blue">
                    {number}
                  </Badge>
                ))}
              </Group>
            </Stack>
            <Divider />
          </>
        )}

        {/* Детали ошибки */}
        {hasError && (
          <Stack gap="xs">
            <Text size="sm" fw={500} c="red">Детали ошибки</Text>
            <Code block>
              {JSON.stringify(request.error_payload, null, 2)}
            </Code>
          </Stack>
        )}

        {/* Raw данные для отладки */}
        {(request.raw_prompt || request.raw_response) && (
          <>
            <Divider />
            <Stack gap="xs">
              <Text size="sm" fw={500}>Отладочная информация</Text>
              
              {request.raw_prompt && (
                <Stack gap="xs">
                  <Text size="xs" fw={500}>Промпт:</Text>
                  <Code block mah={200}>
                    {JSON.stringify(request.raw_prompt, null, 2)}
                  </Code>
                </Stack>
              )}
              
              {request.raw_response && (
                <Stack gap="xs">
                  <Text size="xs" fw={500}>Ответ:</Text>
                  <Code block mah={200}>
                    {JSON.stringify(request.raw_response, null, 2)}
                  </Code>
                </Stack>
              )}
            </Stack>
          </>
        )}
      </Stack>
    </Modal>
  )
}