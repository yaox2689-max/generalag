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
  <!-- 页面背景：浅米白渐变，不承载业务内容 -->
  <div class="page-bg">

    <!-- 主容器：白色底、12px圆角、浅灰边框、柔和阴影，max-width 1200px，上下留白80px -->
    <main class="main-container">

      <!-- ============ 顶部标题区：底部浅灰分割线 ============ -->
      <header class="header-section">
        <div class="header-left">
          <div class="header-icon">
            <Zap :size="18" class="text-terracotta" />
          </div>
          <div>
            <h1 class="header-title">General Agent</h1>
            <p class="header-subtitle">Self-built Plan-and-Execute Engine</p>
          </div>
        </div>
        <div class="status-badge">
          <div class="status-dot"></div>
          <span class="status-text">Ready</span>
        </div>
      </header>

      <!-- ============ 中间内容区（可滚动） ============ -->
      <div ref="scrollEl" class="content-area">

        <!-- Empty state -->
        <div v-if="turns.length === 0" class="empty-state">
          <!-- 图标 -->
          <div class="empty-icon">
            <Zap :size="28" class="text-terracotta/50" />
          </div>

          <!-- 标题 + 描述 -->
          <div class="empty-text">
            <h2 class="empty-title">What can I help with?</h2>
            <p class="empty-desc">A general-purpose agent with pluggable tools.<br>Try a finance query, math problem, or knowledge question.</p>
          </div>

          <!-- 四个快捷按钮：两两分行，每个是独立卡片 -->
          <div class="hints-grid">
            <button
              v-for="h in hints"
              :key="h.query"
              @click="handleSend(h.query)"
              class="hint-card"
            >
              <span class="hint-icon">{{ h.icon }}</span>
              <span class="hint-label">{{ h.label }}</span>
              <p class="hint-query">{{ h.query }}</p>
            </button>
          </div>
        </div>

        <!-- Conversation turns -->
        <template v-for="turn in turns" :key="turn.id">
          <div class="flex justify-end animate-fade-in-up">
            <div class="user-bubble">
              <p>{{ turn.query }}</p>
            </div>
          </div>

          <PipelineView
            :active="turn.activeSteps"
            :done="turn.doneSteps"
            :complexity="turn.complexity"
            :loading="turn.loading"
          />

          <ResultCard v-if="turn.response && !turn.loading" :response="turn.response" />

          <div v-if="turn.loading && turn.doneSteps.length === 0" class="loading-indicator">
            <div class="loading-dots">
              <span class="dot" style="animation-delay:0s"></span>
              <span class="dot" style="animation-delay:0.15s"></span>
              <span class="dot" style="animation-delay:0.3s"></span>
            </div>
            <span class="loading-text">Analyzing your query...</span>
          </div>
        </template>
      </div>

      <!-- ============ 底部输入框区域：独立卡片，和功能区有间距 ============ -->
      <div class="input-section">
        <CommandInput :disabled="isRunning" @send="handleSend" />
      </div>

      <!-- ============ 版本说明：主容器内部最下方 ============ -->
      <footer class="version-footer">
        General Agent v0.1 &mdash; Self-built Plan-and-Execute Engine
      </footer>

    </main>
  </div>
</template>

<style scoped>
/* ======== 页面背景：浅米白渐变，仅作底色 ======== */
.page-bg {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  padding: 80px 24px;                          /* 上下80px留白，左右24px */
  background:
    radial-gradient(ellipse 100% 80% at 30% 0%, rgba(199,92,58,0.05) 0%, transparent 50%),
    radial-gradient(ellipse 80% 60% at 80% 100%, rgba(90,138,106,0.04) 0%, transparent 50%),
    #faf6f1;                                     /* 浅米白底色 */
}

/* ======== 主容器：白色底、圆角、边框、阴影，max-width 1200px ======== */
.main-container {
  width: 100%;
  max-width: 1200px;                            /* 最大宽度限制 */
  min-height: calc(100vh - 160px);              /* 撑满可视区 */
  display: flex;
  flex-direction: column;
  background: #ffffff;                          /* 白色底色 */
  border-radius: 12px;                          /* 12px圆角 */
  border: 1px solid #e5e5e5;                    /* 浅灰实体边框 */
  box-shadow: 0 4px 24px rgba(44, 24, 16, 0.06), 0 1px 4px rgba(44, 24, 16, 0.04); /* 柔和阴影 */
  overflow: hidden;
}

/* ======== 顶部标题区：底部浅灰分割线 ======== */
.header-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 32px;                           /* 内边距 */
  border-bottom: 1px solid #e5e5e5;             /* 浅灰分割线 */
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(199, 92, 58, 0.08);          /* 赤陶浅底 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-title {
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 20px;
  color: #2c1810;                               /* 深咖啡色 */
  letter-spacing: -0.3px;
  margin: 0;
}

.header-subtitle {
  font-size: 12px;
  color: #8a6e55;                               /* 胡桃浅色 */
  margin-top: 1px;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 100px;
  background: rgba(90, 138, 106, 0.08);         /* 鼠尾草绿浅底 */
  border: 1px solid rgba(90, 138, 106, 0.15);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #5a8a6a;                          /* 鼠尾草绿 */
  animation: breathe 2.5s ease-in-out infinite;
}

.status-text {
  font-size: 12px;
  font-weight: 600;
  color: #5a8a6a;
}

/* ======== 中间内容区（可滚动） ======== */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 32px;                                /* 内容区内边距 */
}

/* ======== Empty state ======== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 24px;
  animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.empty-icon {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: rgba(199, 92, 58, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-text {
  text-align: center;
}

.empty-title {
  font-family: 'DM Serif Display', Georgia, serif;
  font-size: 26px;
  color: #2c1810;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #8a6e55;
  line-height: 1.6;
  max-width: 400px;
}

/* ======== 四个快捷按钮：两两分行，每个是独立小卡片 ======== */
.hints-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;               /* 两列 */
  gap: 12px;
  width: 100%;
  max-width: 520px;
  margin-top: 8px;
}

.hint-card {
  text-align: left;
  padding: 18px 20px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid #e5e5e5;                    /* 浅灰边框 */
  cursor: pointer;
  transition: all 0.25s ease;
}

.hint-card:hover {
  border-color: rgba(199, 92, 58, 0.3);         /* hover赤陶边框 */
  box-shadow: 0 4px 16px rgba(199, 92, 58, 0.08); /* hover浅阴影 */
  background: #fff;
}

.hint-icon {
  font-size: 18px;
  display: block;
  margin-bottom: 6px;
}

.hint-label {
  font-size: 14px;
  font-weight: 600;
  color: #2c1810;
  display: block;
}

.hint-card:hover .hint-label {
  color: #c75c3a;                               /* hover赤陶色 */
}

.hint-query {
  font-size: 12px;
  color: #b8a898;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ======== 用户消息气泡 ======== */
.user-bubble {
  max-width: 70%;
  padding: 12px 20px;
  border-radius: 16px 16px 4px 16px;
  background: rgba(199, 92, 58, 0.08);
  border: 1px solid rgba(199, 92, 58, 0.12);
}

.user-bubble p {
  font-size: 14px;
  color: #2c1810;
  line-height: 1.6;
}

/* ======== 加载指示器 ======== */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-left: 8px;
  animation: fadeInUp 0.4s ease both;
}

.loading-dots {
  display: flex;
  gap: 6px;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(199, 92, 58, 0.35);
  animation: bounce 1.2s ease-in-out infinite;
}

.loading-text {
  font-size: 12px;
  color: #8a6e55;
}

/* ======== 底部输入框区域：独立卡片 ======== */
.input-section {
  margin: 0 32px 0;                             /* 左右留白，和内容区对齐 */
  padding: 20px 24px;
  border-radius: 12px;
  background: #faf6f1;                          /* 浅米底，区分白色主容器 */
  border: 1px solid #e5e5e5;                    /* 浅灰边框 */
  flex-shrink: 0;
}

/* ======== 版本说明：主容器内部最下方 ======== */
.version-footer {
  text-align: center;
  font-size: 11px;
  color: #b8a898;
  padding: 12px 0 16px;
  flex-shrink: 0;
}

/* ======== 动画 ======== */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes breathe {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.15); }
}

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}
</style>
