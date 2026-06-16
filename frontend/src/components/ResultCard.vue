<script setup lang="ts">
import { ref } from 'vue'
import type { AgentResponse } from '../types'
import { ChevronDown, Wrench, Clock, Tag } from 'lucide-vue-next'

const props = defineProps<{ response: AgentResponse }>()
const open = ref(false)

const toolIcons: Record<string, string> = {
  financial_report: '📊', web_search: '🔍', calculator: '🧮',
  text_summarizer: '📝', rag_search: '📚', llm_synthesis: '🧠',
}
</script>

<template>
  <div class="rounded-xl border border-warm-600/50 bg-warm-800/60 overflow-hidden">
    <!-- Summary bar -->
    <button
      @click="open = !open"
      class="w-full flex items-center gap-3 px-4 py-2.5 cursor-pointer hover:bg-warm-700/40 transition-colors"
    >
      <div class="flex items-center gap-3 flex-1 text-[11px] text-warm-400">
        <span class="flex items-center gap-1"><Tag :size="12" />{{ response.domain }}</span>
        <span class="flex items-center gap-1"><Clock :size="12" />{{ (response.elapsed_ms / 1000).toFixed(1) }}s</span>
        <span v-if="response.steps.length" class="flex items-center gap-1">
          <Wrench :size="12" />{{ response.steps.length }} tools
        </span>
        <span class="flex gap-1 ml-1">
          <span v-for="s in response.steps" :key="s.task_id" class="text-xs">{{ toolIcons[s.tool] || '⚡' }}</span>
        </span>
      </div>
      <ChevronDown :size="14" class="text-warm-500 transition-transform duration-200" :class="{ 'rotate-180': open }" />
    </button>

    <!-- Expanded details -->
    <Transition name="slide">
      <div v-if="open" class="px-4 pb-3 space-y-2 border-t border-warm-600/30 pt-3">
        <div
          v-for="step in response.steps"
          :key="step.task_id"
          class="flex items-start gap-2.5 p-2.5 rounded-lg bg-warm-700/40 text-xs"
        >
          <span class="text-sm shrink-0">{{ toolIcons[step.tool] || '⚡' }}</span>
          <div class="min-w-0 flex-1">
            <span class="font-mono text-amber-400 text-[11px]">{{ step.tool }}</span>
            <p class="text-warm-400 mt-1 whitespace-pre-wrap line-clamp-3 leading-relaxed">{{ step.output }}</p>
          </div>
        </div>

        <div v-if="response.sources.length" class="flex flex-wrap gap-1.5 pt-1">
          <span v-for="src in response.sources" :key="src"
                class="px-2 py-0.5 text-[11px] rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            {{ src }}
          </span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; overflow: hidden; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; padding-top: 0; padding-bottom: 0; }
.slide-enter-to, .slide-leave-from { max-height: 300px; opacity: 1; }
</style>
