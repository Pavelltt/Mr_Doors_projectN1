import dayjs from 'dayjs'
import type { RequestEvent } from '../hooks/useAnalyticsApi'

export function exportToCSV(data: RequestEvent[], filename: string = 'analytics_export') {
  if (!data.length) {
    alert('Нет данных для экспорта')
    return
  }

  // Заголовки CSV
  const headers = [
    'Request ID',
    'Дата и время',
    'Chat ID',
    'Message ID',
    'Модель',
    'Длительность (сек)',
    'Входные токены',
    'Выходные токены',
    'Стоимость (USD)',
    'Статус',
    'Извлеченные числа',
    'Создано',
  ]

  // Преобразование данных в CSV строки
  const csvRows = [
    headers.join(','), // заголовок
    ...data.map(row => [
      `"${row.request_id}"`,
      `"${dayjs(row.originated_at).format('YYYY-MM-DD HH:mm:ss')}"`,
      `"${row.chat_id || ''}"`,
      `"${row.message_id || ''}"`,
      `"${row.model}"`,
      row.duration_seconds.toFixed(2),
      row.input_tokens,
      row.output_tokens,
      row.cost_usd.toFixed(4),
      `"${row.status}"`,
      `"${row.numbers ? row.numbers.join(', ') : ''}"`,
      `"${dayjs(row.created_at).format('YYYY-MM-DD HH:mm:ss')}"`,
    ].join(','))
  ]

  // Создание и скачивание файла
  const csvContent = csvRows.join('\n')
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `${filename}_${dayjs().format('YYYY-MM-DD_HH-mm')}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

export function exportAggregatedData(
  totalRequests: number,
  totalCost: number,
  totalInputTokens: number,
  totalOutputTokens: number,
  averageLatency: number | null,
  filename: string = 'analytics_summary'
) {
  const headers = ['Метрика', 'Значение']
  
  const summaryData = [
    ['Общее количество запросов', totalRequests.toString()],
    ['Общая стоимость (USD)', `$${totalCost.toFixed(2)}`],
    ['Общее количество входных токенов', totalInputTokens.toLocaleString('ru-RU')],
    ['Общее количество выходных токенов', totalOutputTokens.toLocaleString('ru-RU')],
    ['Средняя задержка (сек)', averageLatency ? averageLatency.toFixed(2) : 'N/A'],
    ['Дата экспорта', dayjs().format('YYYY-MM-DD HH:mm:ss')],
  ]

  const csvRows = [
    headers.join(','),
    ...summaryData.map(row => `"${row[0]}","${row[1]}"`)
  ]

  const csvContent = csvRows.join('\n')
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `${filename}_${dayjs().format('YYYY-MM-DD_HH-mm')}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}