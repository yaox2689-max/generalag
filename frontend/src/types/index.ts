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

export type NodeStatus = 'idle' | 'running' | 'done'

export interface FlowNode {
  id: string
  label: string
  x: number
  y: number
  status: NodeStatus
  detail?: string
}

export interface FlowEdge {
  from: string
  to: string
  active: boolean
}
