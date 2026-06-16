<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import type { ChatMessage } from '../types'
import { User, Bot, Loader2 } from 'lucide-vue-next'

const props = defineProps<{ message: ChatMessage }>()

const isUser = computed(() => props.message.role === 'user')
const renderedContent = computed(() => {
  if (!props.message.content) return ''
  return marked(props.message.content, { breaks: true }) as string
})

const toolIcon: Record<string, string> = {
  financial_report: '📊',
  web_search: '🔍',
  calculator: '🧮',
  text_summarizer: '📝',
  rag_search: '📚',
  llm_synthesis: '🧠',
}
</script>

<template>
  <div
    class="flex gap-3 animate-fade-in-up"
    :class="isUser ? 'flex-row-reverse' : 'flex-row'"
  >
    <!-- Avatar -->
    <div
      class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
      :class="isUser ? 'bg-accent/20' : 'bg-accent/10'"
    >
      <User v-if="isUser" :size="16" class="text-accent-light" />
      <Bot v-else :size="16" class="text-accent" />
    </div>

    <!-- Content -->
    <div class="max-w-[80%] min-w-0">
      <div
        class="rounded-2xl px-4 py-3"
        :class="isUser
          ? 'bg-user-bubble border border-border-light rounded-tr-md'
          : 'bg-ai-bubble border border-border rounded-tl-md'"
      >
        <!-- Loading state -->
        <div v-if="message.loading && !message.content" class="flex items-center gap-2 text-text-secondary">
          <Loader2 :size="16" class="animate-spin" />
          <span class="text-sm">Thinking...</span>
        </div>

        <!-- Content -->
        <div
          v-else
          class="markdown-body text-sm leading-relaxed text-text-primary"
          v-html="renderedContent"
        />

        <!-- Typing cursor -->
        <span
          v-if="message.loading && message.content"
          class="inline-block w-0.5 h-4 bg-accent-light ml-0.5 align-middle animate-pulse"
        />
      </div>

      <!-- Metadata -->
      <div v-if="message.agentResponse && !message.loading" class="mt-2 flex items-center gap-3 text-xs text-text-muted">
        <span class="px-2 py-0.5 rounded-md bg-bg-tertiary border border-border">
          {{ message.agentResponse.domain }}
        </span>
        <span class="px-2 py-0.5 rounded-md bg-bg-tertiary border border-border">
          {{ message.agentResponse.complexity }}
        </span>
        <span v-if="message.agentResponse.elapsed_ms">
          {{ (message.agentResponse.elapsed_ms / 1000).toFixed(1) }}s
        </span>
        <span v-for="step in message.agentResponse.steps" :key="step.task_id">
          {{ toolIcon[step.tool] || '⚡' }}
        </span>
      </div>
    </div>
  </div>
</template>
