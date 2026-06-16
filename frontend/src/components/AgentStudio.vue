<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { sendQuery } from '../api/agent'
import type { AgentResponse } from '../types'
import PipelineView from './PipelineView.vue'
import ResultCard from './ResultCard.vue'
import CommandInput from './CommandInput.vue'
import { Zap } from 'lucide-vue-next'

interface Turn {
  id: string
  query: string
  response?: AgentResponse
  loading: boolean
  activeSteps: string[]
  doneSteps: string[]
  complexity: string
}

const turns = ref<Turn[]>([])
const isRunning = ref(false)
const scrollEl = ref<HTMLElement>()

const uid = () => Math.random().toString(36).slice(2, 8)
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

function scrollToBottom() {
  nextTick(() => { if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight })
}

async function animatePipeline(turn: Turn, complexity: string) {
  const all = ['Router', 'Planner', 'Executor', 'Verifier', 'Writer']
  const steps = complexity === 'simple' ? ['Router', 'Executor', 'Writer'] : all
  turn.activeSteps = []
  turn.doneSteps = []
  turn.complexity = complexity

  for (const s of steps) {
    turn.activeSteps = [s]
    scrollToBottom()
    await sleep(400 + Math.random() * 350)
    turn.activeSteps = []
    turn.doneSteps = [...turn.doneSteps, s]
    scrollToBottom()
  }
}

async function handleSend(query: string) {
  if (isRunning.value) return
  isRunning.value = true

  const turn: Turn = {
    id: uid(), query, loading: true,
    activeSteps: [], doneSteps: [], complexity: '',
  }
  turns.value.push(turn)
  scrollToBottom()

  try {
    const response = await sendQuery(query)
    turn.response = response
    await animatePipeline(turn, response.complexity)
    turn.loading = false
  } catch (err: any) {
    turn.response = {
      answer: `Error: ${err.message}. Is the backend running on :8000?`,
      domain: '', complexity: '', sources: [], steps: [], elapsed_ms: 0,
    }
    turn.loading = false
  } finally {
    isRunning.value = false
    scrollToBottom()
  }
}

const hints = [
  { icon: '📊', label: '财报查询', query: '茅台2024年Q3财报分析' },
  { icon: '🔢', label: '数学计算', query: '计算 2 的 50 次方' },
  { icon: '💡', label: '知识问答', query: '什么是 RAG 技术？' },
  { icon: '⚖️', label: '对比分析', query: '对比比亚迪和特斯拉2024年营收' },
]
</script>

<template>
  <div class="h-full flex justify-center px-6 py-6 overflow-hidden">
    <div class="w-full max-w-[72%] min-w-[640px] h-full flex flex-col">

      <!-- Header -->
      <header class="flex items-center gap-3 mb-5 shrink-0 animate-fade-in-up">
        <div class="w-10 h-10 rounded-2xl bg-terracotta/10 flex items-center justify-center shadow-sm">
          <Zap :size="20" class="text-terracotta" />
        </div>
        <div>
          <h1 class="text-xl font-display text-espresso tracking-tight">General Agent</h1>
          <p class="text-xs text-walnut-light -mt-0.5">Self-built Plan-and-Execute Engine</p>
        </div>
        <div class="ml-auto flex items-center gap-2 px-3 py-1.5 rounded-full bg-sage/10 border border-sage/20">
          <div class="w-1.5 h-1.5 rounded-full bg-sage animate-breathe"></div>
          <span class="text-xs text-sage font-medium">Ready</span>
        </div>
      </header>

      <!-- Scrollable content -->
      <div ref="scrollEl" class="flex-1 overflow-y-auto space-y-5 pb-2">

        <!-- Empty state -->
        <div v-if="turns.length === 0" class="flex flex-col items-center justify-center h-full gap-6 animate-fade-in-up" style="animation-delay: 0.1s">
          <div class="w-16 h-16 rounded-3xl bg-terracotta/8 flex items-center justify-center">
            <Zap :size="30" class="text-terracotta/60" />
          </div>
          <div class="text-center">
            <h2 class="text-2xl font-display text-espresso mb-2">What can I help with?</h2>
            <p class="text-sm text-walnut-light max-w-md">A general-purpose agent with pluggable tools.<br>Try a finance query, math problem, or knowledge question.</p>
          </div>
          <div class="grid grid-cols-2 gap-3 w-full max-w-lg">
            <button
              v-for="(h, i) in hints"
              :key="h.query"
              @click="handleSend(h.query)"
              class="group text-left px-5 py-4 rounded-2xl bg-white/70 border border-parchment
                     hover:border-terracotta/30 hover:bg-white hover:shadow-lg hover:shadow-terracotta/5
                     transition-all duration-300 cursor-pointer"
              :style="{ animationDelay: (0.2 + i * 0.08) + 's' }"
            >
              <span class="text-lg mb-1 block">{{ h.icon }}</span>
              <span class="text-sm font-semibold text-espresso group-hover:text-terracotta transition-colors">{{ h.label }}</span>
              <p class="text-xs text-sand mt-1 truncate">{{ h.query }}</p>
            </button>
          </div>
        </div>

        <!-- Conversation turns -->
        <template v-for="turn in turns" :key="turn.id">
          <!-- User query -->
          <div class="flex justify-end animate-fade-in-up">
            <div class="max-w-[70%] px-5 py-3 rounded-2xl rounded-br-md bg-terracotta/10 border border-terracotta/15">
              <p class="text-sm text-espresso leading-relaxed">{{ turn.query }}</p>
            </div>
          </div>

          <!-- Pipeline visualization -->
          <PipelineView
            :active="turn.activeSteps"
            :done="turn.doneSteps"
            :complexity="turn.complexity"
            :loading="turn.loading"
          />

          <!-- Result card (collapsible) -->
          <ResultCard
            v-if="turn.response && !turn.loading"
            :response="turn.response"
          />

          <!-- Loading indicator -->
          <div v-if="turn.loading && turn.doneSteps.length === 0" class="flex items-center gap-3 ml-2 animate-fade-in-up">
            <div class="flex gap-1.5">
              <span class="w-2 h-2 rounded-full bg-terracotta/40 animate-bounce" style="animation-delay:0s"></span>
              <span class="w-2 h-2 rounded-full bg-terracotta/40 animate-bounce" style="animation-delay:0.15s"></span>
              <span class="w-2 h-2 rounded-full bg-terracotta/40 animate-bounce" style="animation-delay:0.3s"></span>
            </div>
            <span class="text-xs text-walnut-light">Analyzing your query...</span>
          </div>
        </template>
      </div>

      <!-- Command input -->
      <CommandInput :disabled="isRunning" @send="handleSend" />
    </div>
  </div>
</template>
