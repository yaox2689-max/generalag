<script setup lang="ts">
import type { AgentStep } from '../types'
import { Loader2, Check, Circle } from 'lucide-vue-next'

defineProps<{ steps: AgentStep[] }>()
</script>

<template>
  <div class="animate-fade-in-up ml-11">
    <div class="flex items-center gap-1 p-3 rounded-xl bg-bg-secondary border border-border">
      <template v-for="(step, i) in steps" :key="step.name">
        <!-- Step node -->
        <div
          class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs transition-all duration-300"
          :class="{
            'bg-accent/20 text-accent-light border border-accent/30': step.status === 'running',
            'bg-success/10 text-success border border-success/20': step.status === 'done',
            'text-text-muted': step.status === 'pending',
          }"
        >
          <component
            :is="step.status === 'running' ? Loader2 : step.status === 'done' ? Check : Circle"
            :size="14"
            :class="{ 'animate-spin': step.status === 'running' }"
          />
          <span class="font-medium">{{ step.name }}</span>
        </div>

        <!-- Arrow -->
        <div
          v-if="i < steps.length - 1"
          class="w-6 h-px mx-0.5"
          :class="steps[i + 1].status !== 'pending' ? 'bg-accent/40' : 'bg-border'"
        />
      </template>
    </div>
  </div>
</template>
