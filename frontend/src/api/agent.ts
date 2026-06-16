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
