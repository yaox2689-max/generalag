<script setup lang="ts">
import { Route, ListChecks, Play, ShieldCheck, PenLine, Check, Loader2 } from 'lucide-vue-next'

const props = defineProps<{
  active: string[]
  done: string[]
  complexity: string
  loading: boolean
}>()

const steps = [
  { name: 'Router',   icon: Route,       color: 'terracotta' },
  { name: 'Planner',  icon: ListChecks,  color: 'amber' },
  { name: 'Executor', icon: Play,        color: 'sage' },
  { name: 'Verifier', icon: ShieldCheck, color: 'terracotta' },
  { name: 'Writer',   icon: PenLine,     color: 'amber' },
]

function status(name: string) {
  if (props.active.includes(name)) return 'running'
  if (props.done.includes(name)) return 'done'
  return 'idle'
}

const skipInSimple = (name: string) =>
  props.complexity === 'simple' && (name === 'Planner' || name === 'Verifier')
</script>

<template>
  <div class="animate-fade-in-up">
    <div class="flex items-center gap-0 px-2">
      <template v-for="(step, i) in steps" :key="step.name">
        <!-- Step card -->
        <div
          class="relative flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold
                 transition-all duration-400 select-none border"
          :class="{
            'bg-white border-parchment text-sand': status(step.name) === 'idle' && !skipInSimple(step.name),
            'bg-terracotta/8 border-terracotta/25 text-terracotta shadow-sm': status(step.name) === 'running',
            'bg-sage/10 border-sage/25 text-sage': status(step.name) === 'done',
            'opacity-30': skipInSimple(step.name) && status(step.name) === 'idle',
            'line-through opacity-30': skipInSimple(step.name) && status(step.name) !== 'running',
          }"
        >
          <!-- Running pulse ring -->
          <div v-if="status(step.name) === 'running'" class="absolute inset-0 rounded-xl animate-pulse-ring" />

          <Loader2 v-if="status(step.name) === 'running'" :size="14" class="animate-spin relative z-10" />
          <Check v-else-if="status(step.name) === 'done'" :size="14" class="relative z-10" />
          <component v-else :is="step.icon" :size="14" class="relative z-10" />
          <span class="relative z-10">{{ step.name }}</span>
        </div>

        <!-- Connector line -->
        <div
          v-if="i < steps.length - 1"
          class="w-7 h-px mx-0.5 transition-colors duration-400"
          :class="{
            'bg-sage/40': status(steps[i+1].name) === 'done',
            'bg-terracotta/30': status(steps[i+1].name) === 'running',
            'bg-parchment': status(steps[i+1].name) === 'idle',
          }"
        />
      </template>
    </div>
  </div>
</template>
