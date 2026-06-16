<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'
import type { AgentResponse } from '../types'
import { ChevronUp, ChevronDown, Wrench, BookOpen, Clock } from 'lucide-vue-next'

const props = defineProps<{ result: AgentResponse }>()

const expanded = ref(false)

const renderedAnswer = computed(() => {
  return marked(props.result.answer, { breaks: true }) as string
})

const toolIcons: Record<string, string> = {
  financial_report: '📊',
  web_search: '🔍',
  calculator: '🧮',
  text_summarizer: '📝',
  rag_search: '📚',
  llm_synthesis: '🧠',
}
</script>

<template>
  <div class="border-t border-border bg-bg-secondary/80 backdrop-blur-sm shrink-0 transition-all duration-300">
    <!-- Toggle bar -->
    <button
      @click="expanded = !expanded"
      class="w-full flex items-center justify-between px-6 py-2.5 cursor-pointer hover:bg-bg-hover/50 transition-colors"
    >
      <div class="flex items-center gap-4 text-xs text-text-secondary">
        <span class="flex items-center gap-1.5">
          <BookOpen :size="14" />
          Answer ready
        </span>
        <span v-if="result.steps.length" class="flex items-center gap-1.5">
          <Wrench :size="14" />
          {{ result.steps.length }} tool call(s)
        </span>
        <span class="flex items-center gap-1.5">
          <Clock :size="14" />
          {{ (result.elapsed_ms / 1000).toFixed(1) }}s
        </span>
      </div>
      <component :is="expanded ? ChevronDown : ChevronUp" :size="16" class="text-text-muted" />
    </button>

    <!-- Expanded content -->
    <Transition name="expand">
      <div v-if="expanded" class="px-6 pb-4 max-h-[40vh] overflow-y-auto space-y-4">
        <!-- Answer -->
        <div class="markdown-body text-sm" v-html="renderedAnswer" />

        <!-- Tool calls -->
        <div v-if="result.steps.length" class="space-y-2">
          <h4 class="text-xs font-semibold text-text-muted uppercase tracking-wider">Tool Calls</h4>
          <div
            v-for="step in result.steps"
            :key="step.task_id"
            class="flex items-start gap-3 p-3 rounded-lg bg-bg-tertiary border border-border text-xs"
          >
            <span class="text-base shrink-0">{{ toolIcons[step.tool] || '⚡' }}</span>
            <div class="min-w-0 flex-1">
              <span class="font-mono text-accent-light">{{ step.tool }}</span>
              <p class="text-text-secondary mt-1 whitespace-pre-wrap line-clamp-3">{{ step.output }}</p>
            </div>
          </div>
        </div>

        <!-- Sources -->
        <div v-if="result.sources.length" class="flex flex-wrap gap-2">
          <span
            v-for="src in result.sources"
            :key="src"
            class="px-2 py-0.5 text-xs rounded bg-accent/10 text-accent-light border border-accent/20"
          >
            {{ src }}
          </span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.expand-enter-active, .expand-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}
.expand-enter-from, .expand-leave-to {
  max-height: 0;
  opacity: 0;
}
.expand-enter-to, .expand-leave-from {
  max-height: 40vh;
  opacity: 1;
}
</style>
