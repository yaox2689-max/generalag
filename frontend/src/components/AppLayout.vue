<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { sendQuery } from '../api/agent'
import type { AgentResponse } from '../types'
import PipelineFlow from './PipelineFlow.vue'
import ResultCard from './ResultCard.vue'
import CommandInput from './CommandInput.vue'
import { Sparkles, Cpu } from 'lucide-vue-next'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  response?: AgentResponse
  loading?: boolean
}

const messages = ref<Message[]>([])
const activeSteps = ref<string[]>([])
const doneSteps = ref<string[]>([])
const isRunning = ref(false)
const scrollEl = ref<HTMLElement>()

function uid() { return Math.random().toString(36).slice(2, 9) }

function scrollBottom() {
  nextTick(() => { if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight })
}

async function animatePipeline(complexity: string) {
  const allSteps = ['Router', 'Planner', 'Executor', 'Verifier', 'Writer']
  const steps = complexity === 'simple'
    ? ['Router', 'Executor', 'Writer']
    : allSteps

  activeSteps.value = []
  doneSteps.value = []

  for (const s of steps) {
    activeSteps.value = [s]
    await new Promise(r => setTimeout(r, 450 + Math.random() * 350))
    activeSteps.value = []
    doneSteps.value = [...doneSteps.value, s]
  }
}

function typewriterEffect(msg: Message, text: string): Promise<void> {
  return new Promise(resolve => {
    let i = 0
    msg.content = ''
    const tick = () => {
      if (i >= text.length) { resolve(); return }
      msg.content += text[i]
      i++
      if (i % 4 === 0) scrollBottom()
      setTimeout(tick, 12 + Math.random() * 8)
    }
    tick()
  })
}

async function handleSend(query: string) {
  if (isRunning.value) return
  isRunning.value = true

  messages.value.push({ id: uid(), role: 'user', content: query })
  const aiMsg: Message = { id: uid(), role: 'assistant', content: '', loading: true }
  messages.value.push(aiMsg)
  scrollBottom()

  try {
    const [response] = await Promise.all([
      sendQuery(query),
      animatePipeline(''), // start animation, will be refined once response comes
    ])

    // Reset and re-animate with correct complexity
    doneSteps.value = []
    activeSteps.value = []
    await animatePipeline(response.complexity)

    aiMsg.response = response
    aiMsg.loading = false
    await typewriterEffect(aiMsg, response.answer)
    aiMsg.content = response.answer
  } catch (err: any) {
    aiMsg.content = `Error: ${err.message}. Is the backend running on :8000?`
    aiMsg.loading = false
    activeSteps.value = []
    doneSteps.value = []
  } finally {
    isRunning.value = false
    scrollBottom()
  }
}

const quickHints = [
  { label: '财报查询', query: '茅台2024年Q3财报分析' },
  { label: '数学计算', query: '计算 2 的 50 次方' },
  { label: '知识问答', query: '什么是 RAG 技术？' },
  { label: '对比分析', query: '对比比亚迪和特斯拉2024年营收' },
]
</script>

<template>
  <div class="h-full flex items-start justify-center pt-6 pb-4 px-4">
    <div class="w-full max-w-[70%] min-w-[600px] h-[calc(100%-2rem)] flex flex-col rounded-2xl overflow-hidden
                bg-warm-800/80 backdrop-blur-xl border border-warm-600/50
                shadow-[0_8px_60px_rgba(0,0,0,0.4),0_0_120px_rgba(245,158,11,0.03)]">

      <!-- Header -->
      <header class="flex items-center gap-3 px-6 py-3.5 border-b border-warm-600/40 shrink-0">
        <div class="w-8 h-8 rounded-xl bg-amber-500/15 flex items-center justify-center">
          <Cpu :size="16" class="text-amber-400" />
        </div>
        <div class="flex-1">
          <h1 class="text-sm font-semibold text-warm-100 tracking-wide">General Agent</h1>
          <p class="text-[11px] text-warm-400">Self-built Plan-and-Execute Engine</p>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-breathe"></div>
          <span class="text-[11px] text-warm-400">Ready</span>
        </div>
      </header>

      <!-- Pipeline -->
      <PipelineFlow :active="activeSteps" :done="doneSteps" />

      <!-- Messages / Empty state -->
      <div ref="scrollEl" class="flex-1 overflow-y-auto px-6 py-5 space-y-5">
        <!-- Empty -->
        <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full gap-5 animate-fade-in-up">
          <div class="w-14 h-14 rounded-2xl bg-amber-500/10 flex items-center justify-center">
            <Sparkles :size="28" class="text-amber-400" />
          </div>
          <div class="text-center">
            <h2 class="text-lg font-semibold text-warm-100 mb-1">What can I help with?</h2>
            <p class="text-sm text-warm-400 max-w-sm">A general-purpose agent with pluggable tools. Try a finance query, math, or search.</p>
          </div>
          <div class="grid grid-cols-2 gap-2.5 mt-2 w-full max-w-md">
            <button
              v-for="h in quickHints"
              :key="h.query"
              @click="handleSend(h.query)"
              class="group px-4 py-3 text-left rounded-xl border border-warm-600/60 bg-warm-700/40
                     hover:bg-warm-700 hover:border-amber-500/30 transition-all duration-250 cursor-pointer"
            >
              <span class="text-xs font-medium text-warm-300 group-hover:text-amber-400 transition-colors">{{ h.label }}</span>
              <p class="text-[11px] text-warm-500 mt-0.5 truncate">{{ h.query }}</p>
            </button>
          </div>
        </div>

        <!-- Messages -->
        <template v-for="msg in messages" :key="msg.id">
          <!-- User -->
          <div v-if="msg.role === 'user'" class="flex justify-end animate-fade-in-up">
            <div class="max-w-[75%] px-4 py-2.5 rounded-2xl rounded-br-md bg-amber-500/12 border border-amber-500/20">
              <p class="text-sm text-warm-100 leading-relaxed">{{ msg.content }}</p>
            </div>
          </div>

          <!-- Assistant -->
          <div v-else class="flex gap-3 animate-fade-in-up">
            <div class="w-7 h-7 rounded-lg bg-amber-500/10 flex items-center justify-center shrink-0 mt-0.5">
              <Cpu :size="14" class="text-amber-400" />
            </div>
            <div class="flex-1 min-w-0 space-y-3">
              <!-- Loading -->
              <div v-if="msg.loading && !msg.content" class="flex items-center gap-2.5 text-warm-400">
                <div class="flex gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce" style="animation-delay:0s"></span>
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce" style="animation-delay:0.15s"></span>
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-bounce" style="animation-delay:0.3s"></span>
                </div>
                <span class="text-xs">Thinking...</span>
              </div>

              <!-- Content -->
              <div v-else>
                <div class="markdown-body text-sm text-warm-200" v-html="renderMd(msg.content)" />
                <span v-if="msg.loading" class="inline-block w-0.5 h-4 bg-amber-400 ml-0.5 animate-pulse"></span>
              </div>

              <!-- Response meta + tool calls -->
              <ResultCard v-if="msg.response && !msg.loading" :response="msg.response" />
            </div>
          </div>
        </template>
      </div>

      <!-- Input -->
      <CommandInput :disabled="isRunning" @send="handleSend" />
    </div>
  </div>
</template>

<script lang="ts">
import { marked } from 'marked'
function renderMd(text: string): string {
  return marked(text, { breaks: true }) as string
}
export default { methods: { renderMd } }
</script>
