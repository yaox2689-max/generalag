export interface StepResult {
  task_id: number
  tool: string
  output: string
}

export interface AgentResponse {
  answer: string
  domain: string
  complexity: string
  sources: string[]
  steps: StepResult[]
  elapsed_ms: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  agentResponse?: AgentResponse
  loading?: boolean
}

export interface AgentStep {
  name: string
  status: 'pending' | 'running' | 'done'
  detail?: string
}
