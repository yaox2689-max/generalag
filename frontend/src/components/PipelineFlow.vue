<script setup lang="ts">
import { Route, ListChecks, Play, ShieldCheck, PenLine, Check, Loader2 } from 'lucide-vue-next'

const props = defineProps<{
  active: string[]
  done: string[]
}>()

const steps = [
  { name: 'Router',   icon: Route,       label: 'Route' },
  { name: 'Planner',  icon: ListChecks,  label: 'Plan' },
  { name: 'Executor', icon: Play,        label: 'Execute' },
  { name: 'Verifier', icon: ShieldCheck, label: 'Verify' },
  { name: 'Writer',   icon: PenLine,     label: 'Write' },
]

function status(name: string): 'idle' | 'running' | 'done' {
  if (props.active.includes(name)) return 'running'
  if (props.done.includes(name)) return 'done'
  return 'idle'
}
</script>

<template>
  <div class="px-6 py-3 border-b border-warm-600/30 shrink-0">
    <div class="flex items-center justify-center gap-0">
      <template v-for="(step, i) in steps" :key="step.name">
        <!-- Node -->
        <div
          class="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-400 select-none"
          :class="{
            'bg-amber-500/15 text-amber-400 shadow-[0_0_12px_rgba(245,158,11,0.2)]': status(step.name) === 'running',
            'bg-emerald-500/12 text-emerald-500': status(step.name) === 'done',
            'text-warm-500': status(step.name) === 'idle',
          }"
        >
          <Loader2 v-if="status(step.name) === 'running'" :size="13" class="animate-spin" />
          <Check v-else-if="status(step.name) === 'done'" :size="13" />
          <component v-else :is="step.icon" :size="13" />
          <span>{{ step.label }}</span>
        </div>

        <!-- Connector -->
        <div
          v-if="i < steps.length - 1"
          class="w-8 h-px mx-1 transition-colors duration-400"
          :class="status(steps[i + 1].name) !== 'idle' ? 'bg-amber-500/40' : 'bg-warm-600/40'"
        />
      </template>
    </div>
  </div>
</template>
