import axios from 'axios'
import type { AgentResponse } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export async function sendQuery(query: string, useMemory = true): Promise<AgentResponse> {
  const { data } = await api.post<AgentResponse>('/query', { query, use_memory: useMemory })
  return data
}

export async function healthCheck(): Promise<{ status: string; model: string }> {
  const { data } = await api.get('/health')
  return data
}
