<script setup lang="ts">
import { ref, computed } from 'vue'
import { marked } from 'marked'
import type { AgentResponse } from '../types'
import { ChevronDown, Wrench, Clock, Tag, FileText } from 'lucide-vue-next'

const props = defineProps<{ response: AgentResponse }>()
const open = ref(false)

const renderedAnswer = computed(() => marked(props.response.answer, { breaks: true }) as string)

const toolIcons: Record<string, string> = {
  financial_report: '📊', web_search: '🔍', calculator: '🧮',
  text_summarizer: '📝', rag_search: '📚', llm_synthesis: '🧠',
}
</script>

<template>
  <div class="animate-fade-in-up rounded-2xl bg-white/80 border border-parchment shadow-sm overflow-hidden backdrop-blur-sm">
    <!-- Answer preview (always visible) -->
    <div class="px-5 py-4">
      <div class="markdown-body text-sm" v-html="renderedAnswer" />
    </div>

    <!-- Toggle details -->
    <button
      @click="open = !open"
      class="w-full flex items-center gap-3 px-5 py-2.5 border-t border-parchment/60
             bg-cream-dark/40 hover:bg-cream-dark/70 transition-colors cursor-pointer"
    >
      <div class="flex items-center gap-4 flex-1 text-[11px] text-walnut-light">
        <span class="flex items-center gap-1.5">
          <Tag :size="12" class="text-terracotta/60" />
          {{ response.domain || 'general' }}
        </span>
        <span class="flex items-center gap-1.5">
          <Clock :size="12" class="text-amber/60" />
          {{ (response.elapsed_ms / 1000).toFixed(1) }}s
        </span>
        <span v-if="response.steps.length" class="flex items-center gap-1.5">
          <Wrench :size="12" class="text-sage/60" />
          {{ response.steps.length }} tool call{{ response.steps.length > 1 ? 's' : '' }}
        </span>
        <span class="flex gap-1">
          <span v-for="s in response.steps" :key="s.task_id">{{ toolIcons[s.tool] || '⚡' }}</span>
        </span>
      </div>
      <div class="flex items-center gap-1.5 text-xs text-walnut-light">
        <FileText :size="12" />
        <span>Details</span>
        <ChevronDown :size="14" class="transition-transform duration-300" :class="{ 'rotate-180': open }" />
      </div>
    </button>

    <!-- Expandable details -->
    <Transition name="expand">
      <div v-if="open" class="border-t border-parchment/60">
        <!-- Tool calls -->
        <div v-if="response.steps.length" class="px-5 py-4 space-y-2.5">
          <h4 class="text-xs font-semibold text-walnut uppercase tracking-wider mb-3">Tool Calls</h4>
          <div
            v-for="(step, i) in response.steps"
            :key="step.task_id"
            class="flex items-start gap-3 p-3 rounded-xl bg-cream-dark/60 border border-parchment/50"
          >
            <span class="text-base shrink-0 mt-0.5">{{ toolIcons[step.tool] || '⚡' }}</span>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <span class="text-xs font-mono font-semibold text-terracotta">{{ step.tool }}</span>
                <span class="text-[10px] text-sand">Step {{ i + 1 }}</span>
              </div>
              <p class="text-xs text-walnut-light mt-1.5 whitespace-pre-wrap leading-relaxed line-clamp-3">{{ step.output }}</p>
            </div>
          </div>
        </div>

        <!-- Sources -->
        <div v-if="response.sources.length" class="px-5 pb-4 flex flex-wrap gap-1.5">
          <span class="text-[11px] text-walnut-light mr-1">Sources:</span>
          <span
            v-for="src in response.sources"
            :key="src"
            class="px-2.5 py-0.5 text-[11px] rounded-full bg-terracotta/8 text-terracotta border border-terracotta/15"
          >
            {{ src }}
          </span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.expand-enter-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); overflow: hidden; }
.expand-leave-active { transition: all 0.2s ease; overflow: hidden; }
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0; }
.expand-enter-to { max-height: 500px; opacity: 1; }
</style>
