<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { sendQuery } from '../api/agent'
import type { AgentResponse } from '../types'
import ExecutionPanel from './ExecutionPanel.vue'
import CommandInput from './CommandInput.vue'
import { Zap, Route, ListChecks, Play, ShieldCheck, PenLine } from 'lucide-vue-next'

interface Turn {
  id: string
  query: string
  response?: AgentResponse
  loading: boolean
  activeStep: string
  doneSteps: string[]
  complexity: string
  stepDetails: Record<string, string>
}

const turns = ref<Turn[]>([])
const isRunning = ref(false)
const scrollEl = ref<HTMLElement>()

const uid = () => Math.random().toString(36).slice(2, 8)
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

function scrollToBottom() {
  nextTick(() => { if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight })
}

const stepMeta: Record<string, { icon: any; desc: string }> = {
  Router:   { icon: Route,       desc: 'Identifying domain and complexity' },
  Planner:  { icon: ListChecks,  desc: 'Decomposing into subtasks' },
  Executor: { icon: Play,        desc: 'Calling tools and executing steps' },
  Verifier: { icon: ShieldCheck, desc: 'Verifying result completeness' },
  Writer:   { icon: PenLine,     desc: 'Generating structured answer' },
}

async function animatePipeline(turn: Turn, response: AgentResponse) {
  const all = ['Router', 'Planner', 'Executor', 'Verifier', 'Writer']
  const steps = response.complexity === 'simple' ? ['Router', 'Executor', 'Writer'] : all
  turn.activeStep = ''
  turn.doneSteps = []
  turn.complexity = response.complexity
  turn.stepDetails = {}

  for (const s of steps) {
    turn.activeStep = s
    scrollToBottom()
    await sleep(500 + Math.random() * 400)
    turn.activeStep = ''
    turn.doneSteps = [...turn.doneSteps, s]

    // Attach step detail from response
    if (s === 'Router') turn.stepDetails[s] = `Domain: ${response.domain} | ${response.complexity}`
    if (s === 'Planner') turn.stepDetails[s] = `${response.steps.length} subtask(s) planned`
    if (s === 'Executor') {
      const tools = [...new Set(response.steps.map(st => st.tool))].join(', ')
      turn.stepDetails[s] = `Tools: ${tools}`
    }
    if (s === 'Verifier') turn.stepDetails[s] = 'Result verified'
    if (s === 'Writer') turn.stepDetails[s] = `Answer generated (${(response.elapsed_ms / 1000).toFixed(1)}s)`
    scrollToBottom()
  }
}

async function handleSend(query: string) {
  if (isRunning.value) return
  isRunning.value = true

  const turn: Turn = {
    id: uid(), query, loading: true,
    activeStep: '', doneSteps: [], complexity: '', stepDetails: {},
  }
  turns.value.push(turn)
  scrollToBottom()

  try {
    const response = await sendQuery(query)
    turn.response = response
    await animatePipeline(turn, response)
    turn.loading = false
  } catch (err: any) {
    turn.response = {
      answer: `Error: ${err.message}. Is the backend running on :8000?`,
      domain: '', complexity: '', sources: [], steps: [], elapsed_ms: 0,
    }
    turn.doneSteps = ['Router']
    turn.stepDetails['Router'] = 'Error occurred'
    turn.loading = false
  } finally {
    isRunning.value = false
    scrollToBottom()
  }
}

const hints = [
  { icon: '📊', label: 'Financial Report', query: '茅台2024年Q3财报分析', tag: 'finance' },
  { icon: '🔢', label: 'Math Calculation', query: '计算 2 的 50 次方', tag: 'calculator' },
  { icon: '💡', label: 'Knowledge QA', query: '什么是 RAG 技术？', tag: 'qa' },
  { icon: '⚖️', label: 'Comparison', query: '对比比亚迪和特斯拉2024年营收', tag: 'analysis' },
]
</script>

<template>
  <div class="page-bg">
    <main class="main-container">

      <!-- Header -->
      <header class="header-section">
        <div class="header-left">
          <div class="header-icon"><Zap :size="18" class="text-terracotta" /></div>
          <div>
            <h1 class="header-title">General Agent</h1>
            <p class="header-subtitle">Plan-and-Execute · Pluggable Tools · Self-Verification</p>
          </div>
        </div>
        <div class="status-badge">
          <div class="status-dot"></div>
          <span class="status-text">{{ isRunning ? 'Running...' : 'Ready' }}</span>
        </div>
      </header>

      <!-- Content -->
      <div ref="scrollEl" class="content-area">

        <!-- Empty state -->
        <div v-if="turns.length === 0" class="empty-state">
          <div class="empty-hero">
            <div class="empty-icon"><Zap :size="32" class="text-terracotta" /></div>
            <h2 class="empty-title">What can I help with?</h2>
            <p class="empty-desc">A domain-agnostic agent that plans, executes tools, and verifies its own answers.</p>
          </div>

          <!-- Architecture preview -->
          <div class="arch-preview">
            <div class="arch-step" v-for="name in ['Router','Planner','Executor','Verifier','Writer']" :key="name">
              <component :is="stepMeta[name].icon" :size="16" class="arch-step-icon" />
              <span class="arch-step-name">{{ name }}</span>
            </div>
          </div>

          <!-- Hints -->
          <div class="hints-grid">
            <button v-for="h in hints" :key="h.query" @click="handleSend(h.query)" class="hint-card">
              <div class="hint-top">
                <span class="hint-icon">{{ h.icon }}</span>
                <span class="hint-tag">{{ h.tag }}</span>
              </div>
              <span class="hint-label">{{ h.label }}</span>
              <p class="hint-query">{{ h.query }}</p>
            </button>
          </div>
        </div>

        <!-- Conversation turns -->
        <template v-for="(turn, turnIdx) in turns" :key="turn.id">
          <div class="turn-group">
            <!-- Turn number badge -->
            <div class="turn-header">
              <span class="turn-badge">Turn {{ turnIdx + 1 }}</span>
            </div>

            <!-- User query -->
            <div class="user-query">
              <p>{{ turn.query }}</p>
            </div>

            <!-- Execution panel: the hero component -->
            <ExecutionPanel
              :active-step="turn.activeStep"
              :done-steps="turn.doneSteps"
              :complexity="turn.complexity"
              :step-details="turn.stepDetails"
              :response="turn.response || null"
              :loading="turn.loading"
            />
          </div>
        </template>
      </div>

      <!-- Input -->
      <div class="input-section">
        <CommandInput :disabled="isRunning" @send="handleSend" />
      </div>

      <footer class="version-footer">
        General Agent v0.1 · Self-built Plan-and-Execute Engine
      </footer>
    </main>
  </div>
</template>

<style scoped>
.page-bg {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 60px 24px 40px;
  background:
    radial-gradient(ellipse 100% 80% at 30% 0%, rgba(199,92,58,0.05) 0%, transparent 50%),
    radial-gradient(ellipse 80% 60% at 80% 100%, rgba(90,138,106,0.04) 0%, transparent 50%),
    #faf6f1;
}

.main-container {
  width: 100%;
  max-width: 1200px;
  min-height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e5e5;
  box-shadow: 0 4px 24px rgba(44,24,16,0.06), 0 1px 4px rgba(44,24,16,0.04);
  overflow: hidden;
}

/* Header */
.header-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 36px;
  border-bottom: 1px solid #e5e5e5;
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 14px; }
.header-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: rgba(199,92,58,0.08);
  display: flex; align-items: center; justify-content: center;
}
.header-title {
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 20px; color: #2c1810; letter-spacing: -0.3px; margin: 0;
}
.header-subtitle { font-size: 12px; color: #8a6e55; margin-top: 2px; }
.status-badge {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 14px; border-radius: 100px;
  background: rgba(90,138,106,0.08);
  border: 1px solid rgba(90,138,106,0.15);
}
.status-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #5a8a6a;
  animation: breathe 2.5s ease-in-out infinite;
}
.status-text { font-size: 12px; font-weight: 600; color: #5a8a6a; }

/* Content */
.content-area { flex: 1; overflow-y: auto; padding: 36px; }

/* Empty state */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 32px; padding: 24px 0;
  animation: fadeInUp 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
.empty-hero { text-align: center; }
.empty-icon {
  width: 72px; height: 72px; border-radius: 22px;
  background: rgba(199,92,58,0.07);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 20px;
}
.empty-title {
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 28px; color: #2c1810; margin-bottom: 10px;
}
.empty-desc { font-size: 14px; color: #8a6e55; line-height: 1.6; max-width: 420px; margin: 0 auto; }

/* Architecture preview - horizontal step bar */
.arch-preview {
  display: flex; align-items: center; gap: 0;
  padding: 14px 20px; border-radius: 12px;
  background: #faf6f1; border: 1px solid #e5e5e5;
}
.arch-step {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: 8px;
  font-size: 12px; font-weight: 600; color: #6b4f3a;
}
.arch-step-icon { color: #c75c3a; }
.arch-step-name { white-space: nowrap; }
.arch-preview .arch-step + .arch-step::before {
  content: '→'; margin-right: 6px; color: #d4c8b8; font-weight: 400;
}

/* Hints grid */
.hints-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 14px; width: 100%; max-width: 560px;
}
.hint-card {
  text-align: left; padding: 20px;
  border-radius: 12px; background: #ffffff;
  border: 1px solid #e5e5e5;
  cursor: pointer; transition: all 0.25s ease;
}
.hint-card:hover {
  border-color: rgba(199,92,58,0.3);
  box-shadow: 0 6px 20px rgba(199,92,58,0.08);
}
.hint-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.hint-icon { font-size: 20px; }
.hint-tag {
  font-size: 10px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.5px; color: #c75c3a;
  padding: 2px 8px; border-radius: 4px;
  background: rgba(199,92,58,0.08);
}
.hint-label {
  font-size: 14px; font-weight: 600; color: #2c1810; display: block; margin-bottom: 4px;
}
.hint-card:hover .hint-label { color: #c75c3a; }
.hint-query {
  font-size: 12px; color: #b8a898; line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

/* Turn groups */
.turn-group {
  margin-bottom: 28px;
  padding-bottom: 28px;
  border-bottom: 1px solid #f0ebe4;
}
.turn-group:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }

.turn-header { margin-bottom: 12px; }
.turn-badge {
  font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.8px; color: #b8a898;
}

.user-query {
  display: inline-block; max-width: 75%;
  padding: 12px 20px; margin-bottom: 16px;
  border-radius: 14px 14px 14px 4px;
  background: rgba(199,92,58,0.07);
  border: 1px solid rgba(199,92,58,0.12);
}
.user-query p { font-size: 14px; color: #2c1810; line-height: 1.6; margin: 0; }

/* Input */
.input-section {
  margin: 0 36px; padding: 20px 24px;
  border-radius: 12px; background: #faf6f1;
  border: 1px solid #e5e5e5; flex-shrink: 0;
}

/* Footer */
.version-footer {
  text-align: center; font-size: 11px; color: #b8a898;
  padding: 14px 0 18px; flex-shrink: 0;
}

/* Animations */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes breathe {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.15); }
}
</style>
