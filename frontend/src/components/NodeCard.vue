<script setup lang="ts">
import { computed } from 'vue'
import type { FlowNode } from '../types'
import { Route, ListChecks, Play, ShieldCheck, PenLine, Loader2, Check, Circle } from 'lucide-vue-next'

const props = defineProps<{
  node: FlowNode
  selected: boolean
}>()

const iconMap: Record<string, any> = {
  router: Route,
  planner: ListChecks,
  executor: Play,
  verifier: ShieldCheck,
  writer: PenLine,
}

const statusIcon = computed(() => {
  if (props.node.status === 'running') return Loader2
  if (props.node.status === 'done') return Check
  return Circle
})

const statusColor = computed(() => {
  if (props.node.status === 'running') return 'border-accent bg-accent/15 shadow-[0_0_24px_rgba(108,92,231,0.3)]'
  if (props.node.status === 'done') return 'border-success/50 bg-success/10 shadow-[0_0_16px_rgba(0,184,148,0.15)]'
  return 'border-border bg-bg-secondary'
})

const WIDTH = 220
</script>

<template>
  <div
    :style="{ width: WIDTH + 'px' }"
    class="rounded-xl border-2 cursor-pointer transition-all duration-300 select-none hover:scale-[1.03] active:scale-[0.98]"
    :class="[statusColor, selected ? 'ring-2 ring-accent/50' : '']"
  >
    <div class="flex items-center gap-3 px-4 py-3">
      <div
        class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-colors duration-300"
        :class="node.status === 'done' ? 'bg-success/20' : node.status === 'running' ? 'bg-accent/20' : 'bg-bg-tertiary'"
      >
        <component
          :is="iconMap[node.id] || Circle"
          :size="18"
          :class="node.status === 'done' ? 'text-success' : node.status === 'running' ? 'text-accent-light' : 'text-text-muted'"
        />
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-sm font-semibold" :class="node.status === 'idle' ? 'text-text-muted' : 'text-text-primary'">
          {{ node.label }}
        </div>
        <div v-if="node.detail" class="text-xs text-text-secondary truncate mt-0.5">{{ node.detail }}</div>
      </div>
      <component
        :is="statusIcon"
        :size="16"
        :class="[
          node.status === 'running' ? 'text-accent-light animate-spin' : '',
          node.status === 'done' ? 'text-success' : '',
          node.status === 'idle' ? 'text-text-muted/50' : '',
        ]"
      />
    </div>
  </div>
</template>
