import axios from 'axios'
import type { AgentResponse } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export async function sendQuery(query: string): Promise<AgentResponse> {
  const { data } = await api.post<AgentResponse>('/query', { query })
  return data
}

export interface StreamEvent {
  type: 'step_start' | 'step_done' | 'final_answer'
  step?: string
  detail?: string
  answer?: string
  domain?: string
  complexity?: string
  sources?: string[]
  steps?: { task_id: number; tool: string; output: string }[]
  elapsed_ms?: number
}

export async function sendQueryStream(
  query: string,
  onEvent: (event: StreamEvent) => void,
): Promise<void> {
  const response = await fetch('/api/query/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })

  if (!response.ok || !response.body) {
    throw new Error(`Stream failed: ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      try {
        const event = JSON.parse(line.slice(6)) as StreamEvent
        onEvent(event)
      } catch { /* skip malformed */ }
    }
  }
}
