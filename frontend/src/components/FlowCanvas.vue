<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { sendQuery } from '../api/agent'
import type { FlowNode, FlowEdge, AgentResponse } from '../types'
import NodeCard from './NodeCard.vue'
import ResultPanel from './ResultPanel.vue'
import CommandBar from './CommandBar.vue'
import { Zap } from 'lucide-vue-next'

// Node positions (centered in canvas)
const W = 220, H = 72
const CX = 400  // center X

const nodes = reactive<FlowNode[]>([
  { id: 'router',   label: 'Router',   x: CX,         y: 40,  status: 'idle' },
  { id: 'planner',  label: 'Planner',  x: CX - 160,   y: 160, status: 'idle' },
  { id: 'executor', label: 'Executor', x: CX - 160,   y: 280, status: 'idle' },
  { id: 'verifier', label: 'Verifier', x: CX - 160,   y: 400, status: 'idle' },
  { id: 'writer',   label: 'Writer',   x: CX,         y: 520, status: 'idle' },
])

// Edges for complex path
const edges = reactive<FlowEdge[]>([
  { from: 'router', to: 'planner',  active: false },
  { from: 'planner', to: 'executor', active: false },
  { from: 'executor', to: 'verifier', active: false },
  { from: 'verifier', to: 'planner',  active: false },  // retry loop
  { from: 'verifier', to: 'writer',   active: false },
  { from: 'router', to: 'executor',  active: false },    // simple fast path
  { from: 'executor', to: 'writer',   active: false },    // simple fast path
])

const selectedNode = ref<FlowNode | null>(null)
const result = ref<AgentResponse | null>(null)
const isRunning = ref(false)
const domain = ref('')
const complexity = ref('')

function resetNodes() {
  nodes.forEach(n => { n.status = 'idle'; n.detail = undefined })
  edges.forEach(e => { e.active = false })
  selectedNode.value = null
  result.value = null
}

function getEdgePath(from: FlowNode, to: FlowNode): string {
  const fx = from.x + W / 2
  const fy = from.y + H
  const tx = to.x + W / 2
  const ty = to.y
  const my = (fy + ty) / 2
  return `M ${fx} ${fy} C ${fx} ${my}, ${tx} ${my}, ${tx} ${ty}`
}

async function animateStep(nodeId: string, detail?: string) {
  const node = nodes.find(n => n.id === nodeId)
  if (!node) return
  node.status = 'running'
  await new Promise(r => setTimeout(r, 500 + Math.random() * 400))
  node.status = 'done'
  if (detail) node.detail = detail
}

function activateEdge(fromId: string, toId: string) {
  const edge = edges.find(e => e.from === fromId && e.to === toId)
  if (edge) edge.active = true
}

async function handleSend(query: string) {
  if (isRunning.value) return
  isRunning.value = true
  resetNodes()

  // Start API call in parallel with animation
  const apiPromise = sendQuery(query)

  // Animate router first
  await animateStep('router', `Domain detected: analyzing...`)

  try {
    const response = await apiPromise
    result.value = response
    domain.value = response.domain
    complexity.value = response.complexity

    const isSimple = response.complexity === 'simple'

    if (isSimple) {
      // Simple path: router → executor → writer
      nodes.find(n => n.id === 'planner')!.status = 'idle'
      nodes.find(n => n.id === 'verifier')!.status = 'idle'
      nodes.find(n => n.id === 'router')!.detail = `Domain: ${response.domain} | Simple`

      activateEdge('router', 'executor')
      await animateStep('executor', `${response.steps.length} tool(s) called`)

      activateEdge('executor', 'writer')
      await animateStep('writer', 'Answer generated')
    } else {
      // Complex path: router → planner → executor → verifier → writer
      nodes.find(n => n.id === 'router')!.detail = `Domain: ${response.domain} | Complex`

      activateEdge('router', 'planner')
      await animateStep('planner', `${response.steps.length} subtask(s) planned`)

      activateEdge('planner', 'executor')
      const toolNames = [...new Set(response.steps.map(s => s.tool))].join(', ')
      await animateStep('executor', `Tools: ${toolNames}`)

      activateEdge('executor', 'verifier')
      await animateStep('verifier', `Score: verified`)

      activateEdge('verifier', 'writer')
      await animateStep('writer', 'Answer generated')
    }
  } catch (err: any) {
    nodes.forEach(n => {
      if (n.status === 'running') n.status = 'idle'
    })
    result.value = {
      answer: `Error: ${err.message}`,
      domain: '', complexity: '', sources: [], steps: [], elapsed_ms: 0,
    }
  } finally {
    isRunning.value = false
  }
}

function handleNodeClick(node: FlowNode) {
  if (node.status === 'done' && node.detail) {
    selectedNode.value = selectedNode.value?.id === node.id ? null : node
  }
}

const totalMs = computed(() => result.value?.elapsed_ms ?? 0)
</script>

<template>
  <div class="h-full flex flex-col bg-bg-primary overflow-hidden">
    <!-- Header -->
    <header class="flex items-center justify-between px-6 py-3 border-b border-border shrink-0 z-10">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center">
          <Zap :size="18" class="text-accent-light" />
        </div>
        <span class="text-sm font-semibold text-text-primary tracking-wide">GENERAL AGENT</span>
      </div>
      <div class="flex items-center gap-4 text-xs text-text-muted">
        <span v-if="domain" class="px-2 py-0.5 rounded bg-bg-tertiary border border-border">{{ domain }}</span>
        <span v-if="complexity" class="px-2 py-0.5 rounded bg-bg-tertiary border border-border">{{ complexity }}</span>
        <span v-if="totalMs">{{ (totalMs / 1000).toFixed(1) }}s</span>
      </div>
    </header>

    <!-- Canvas -->
    <div class="flex-1 relative overflow-hidden">
      <svg class="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <!-- Edges -->
        <path
          v-for="edge in edges"
          :key="`${edge.from}-${edge.to}`"
          :d="getEdgePath(
            nodes.find(n => n.id === edge.from)!,
            nodes.find(n => n.id === edge.to)!
          )"
          fill="none"
          :stroke="edge.active ? '#6c5ce7' : '#2a2a3a'"
          :stroke-width="edge.active ? 2.5 : 1.5"
          :stroke-dasharray="edge.active ? '8 4' : 'none'"
          :filter="edge.active ? 'url(#glow)' : ''"
          class="transition-all duration-500"
          :class="{ 'edge-flow': edge.active }"
        />

        <!-- Arrowheads for active edges -->
        <circle
          v-for="edge in edges.filter(e => e.active)"
          :key="`dot-${edge.from}-${edge.to}`"
          r="4"
          fill="#a29bfe"
          filter="url(#glow)"
          class="edge-dot"
        >
          <animateMotion
            :dur="`${1 + Math.random()}s`"
            repeatCount="indefinite"
            :path="getEdgePath(
              nodes.find(n => n.id === edge.from)!,
              nodes.find(n => n.id === edge.to)!
            )"
          />
        </circle>
      </svg>

      <!-- Node cards -->
      <NodeCard
        v-for="node in nodes"
        :key="node.id"
        :node="node"
        :selected="selectedNode?.id === node.id"
        :style="{ position: 'absolute', left: node.x + 'px', top: node.y + 'px' }"
        @click="handleNodeClick(node)"
      />

      <!-- Node detail popup -->
      <Transition name="slide">
        <div
          v-if="selectedNode"
          class="absolute top-4 right-4 w-80 max-h-[60%] bg-bg-secondary border border-border-light rounded-xl
                 shadow-2xl overflow-hidden z-20 animate-slide-in-right"
        >
          <div class="flex items-center justify-between px-4 py-3 border-b border-border">
            <span class="text-sm font-semibold text-text-primary">{{ selectedNode.label }} Output</span>
            <button @click="selectedNode = null" class="text-text-muted hover:text-text-primary cursor-pointer text-lg">&times;</button>
          </div>
          <div class="p-4 overflow-y-auto max-h-[calc(100%-48px)]">
            <pre class="text-xs text-text-secondary whitespace-pre-wrap leading-relaxed font-mono">{{ selectedNode.detail }}</pre>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Result panel -->
    <ResultPanel v-if="result" :result="result" />

    <!-- Command bar -->
    <CommandBar :disabled="isRunning" @send="handleSend" />
  </div>
</template>

<style scoped>
@keyframes edgeFlow {
  to { stroke-dashoffset: -24; }
}
.edge-flow {
  animation: edgeFlow 0.8s linear infinite;
}

.slide-enter-active, .slide-leave-active {
  transition: all 0.25s ease;
}
.slide-enter-from, .slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
