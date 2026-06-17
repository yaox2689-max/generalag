<script setup lang="ts">
import { ref } from 'vue'
import { marked } from 'marked'
import type { AgentResponse } from '../types'
import {
  Route, ListChecks, Play, ShieldCheck, PenLine,
  Check, Loader2, Circle, ChevronRight, Clock, Wrench
} from 'lucide-vue-next'

const props = defineProps<{
  activeStep: string
  doneSteps: string[]
  complexity: string
  stepDetails: Record<string, string>
  response: AgentResponse | null
  loading: boolean
}>()

const expandedStep = ref<string | null>(null)

const steps = [
  { name: 'Router',   icon: Route,       desc: 'Domain & complexity detection' },
  { name: 'Planner',  icon: ListChecks,  desc: 'Task decomposition' },
  { name: 'Executor', icon: Play,        desc: 'Tool execution' },
  { name: 'Verifier', icon: ShieldCheck, desc: 'Result verification' },
  { name: 'Writer',   icon: PenLine,     desc: 'Answer generation' },
]

const toolIcons: Record<string, string> = {
  financial_report: '📊', web_search: '🔍', calculator: '🧮',
  text_summarizer: '📝', rag_search: '📚', llm_synthesis: '🧠',
}

function stepStatus(name: string) {
  if (props.activeStep === name) return 'running'
  if (props.doneSteps.includes(name)) return 'done'
  return 'idle'
}

function isVisible(name: string) {
  if (props.complexity === 'simple') {
    return name === 'Router' || name === 'Executor' || name === 'Writer'
  }
  return true
}

function toggleExpand(name: string) {
  if (stepStatus(name) !== 'done') return
  expandedStep.value = expandedStep.value === name ? null : name
}

function renderedAnswer(text: string) {
  return marked(text, { breaks: true }) as string
}
</script>

<template>
  <div class="exec-panel">
    <!-- Steps -->
    <div class="steps-list">
      <template v-for="(step, i) in steps" :key="step.name">
        <div
          v-if="isVisible(step.name)"
          class="step-row"
          :class="{
            'step-running': stepStatus(step.name) === 'running',
            'step-done': stepStatus(step.name) === 'done',
            'step-idle': stepStatus(step.name) === 'idle',
          }"
          @click="toggleExpand(step.name)"
        >
          <!-- Status icon -->
          <div class="step-icon-wrap">
            <div v-if="stepStatus(step.name) === 'running'" class="step-pulse"></div>
            <Loader2 v-if="stepStatus(step.name) === 'running'" :size="16" class="step-icon spinning" />
            <Check v-else-if="stepStatus(step.name) === 'done'" :size="16" class="step-icon" />
            <Circle v-else :size="16" class="step-icon" />
          </div>

          <!-- Content -->
          <div class="step-content">
            <div class="step-header">
              <span class="step-name">{{ step.name }}</span>
              <span v-if="stepStatus(step.name) === 'done' && stepDetails[step.name]" class="step-detail">
                {{ stepDetails[step.name] }}
              </span>
              <ChevronRight
                v-if="stepStatus(step.name) === 'done' && step.name === 'Executor' && response?.steps?.length"
                :size="14"
                class="step-expand-icon"
                :class="{ rotated: expandedStep === step.name }"
              />
            </div>
            <p class="step-desc">{{ step.desc }}</p>

            <!-- Expandable: tool call details for Executor -->
            <Transition name="slide">
              <div v-if="expandedStep === step.name && step.name === 'Executor' && response" class="step-detail-panel">
                <div v-for="s in response.steps" :key="s.task_id" class="tool-call-item">
                  <span class="tool-icon">{{ toolIcons[s.tool] || '⚡' }}</span>
                  <div class="tool-info">
                    <span class="tool-name">{{ s.tool }}</span>
                    <p class="tool-output">{{ s.output }}</p>
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <!-- Connector -->
          <div v-if="i < steps.filter(s => isVisible(s.name)).length - 1" class="step-connector"></div>
        </div>
      </template>
    </div>

    <!-- Result: embedded at the bottom of the panel -->
    <Transition name="slide">
      <div v-if="response && !loading" class="result-section">
        <div class="result-header">
          <div class="result-meta">
            <span class="meta-tag">{{ response.domain || 'general' }}</span>
            <span class="meta-tag">{{ response.complexity }}</span>
            <span class="meta-time">
              <Clock :size="12" />
              {{ (response.elapsed_ms / 1000).toFixed(1) }}s
            </span>
            <span v-if="response.steps.length" class="meta-time">
              <Wrench :size="12" />
              {{ response.steps.length }} tools
            </span>
          </div>
        </div>
        <div class="result-answer markdown-body" v-html="renderedAnswer(response.answer)"></div>

        <!-- Sources -->
        <div v-if="response.sources.length" class="result-sources">
          <span v-for="src in response.sources" :key="src" class="source-tag">{{ src }}</span>
        </div>
      </div>
    </Transition>

    <!-- Loading -->
    <div v-if="loading && doneSteps.length === 0" class="loading-bar">
      <div class="loading-bar-inner"></div>
    </div>
  </div>
</template>

<style scoped>
.exec-panel {
  background: #faf6f1;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 20px 24px;
  margin-top: 12px;
}

/* Steps */
.steps-list { display: flex; flex-direction: column; gap: 0; }

.step-row {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 10px 12px; border-radius: 10px;
  transition: all 0.25s ease; position: relative;
  cursor: default;
}
.step-row.step-done { cursor: pointer; }
.step-row.step-done:hover { background: rgba(199,92,58,0.04); }
.step-row.step-running { background: rgba(199,92,58,0.06); }

/* Icon */
.step-icon-wrap {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; position: relative;
}
.step-idle .step-icon-wrap { background: #f0ebe4; }
.step-done .step-icon-wrap { background: rgba(90,138,106,0.12); }
.step-running .step-icon-wrap { background: rgba(199,92,58,0.12); }

.step-icon { position: relative; z-index: 1; }
.step-idle .step-icon { color: #b8a898; }
.step-done .step-icon { color: #5a8a6a; }
.step-running .step-icon { color: #c75c3a; }
.spinning { animation: spin 1s linear infinite; }

.step-pulse {
  position: absolute; inset: -4px; border-radius: 12px;
  border: 2px solid rgba(199,92,58,0.2);
  animation: pulseRing 1.5s ease-out infinite;
}

/* Content */
.step-content { flex: 1; min-width: 0; }
.step-header { display: flex; align-items: center; gap: 10px; }
.step-name {
  font-size: 13px; font-weight: 600;
  color: #2c1810;
}
.step-idle .step-name { color: #b8a898; }

.step-detail {
  font-size: 11px; color: #8a6e55;
  background: rgba(199,92,58,0.06);
  padding: 2px 8px; border-radius: 4px;
}
.step-expand-icon {
  color: #b8a898; transition: transform 0.2s ease; margin-left: auto;
}
.step-expand-icon.rotated { transform: rotate(90deg); }

.step-desc { font-size: 11px; color: #b8a898; margin-top: 2px; }
.step-done .step-desc { color: #8a6e55; }

/* Tool detail panel */
.step-detail-panel {
  margin-top: 10px; padding: 12px;
  background: #ffffff; border: 1px solid #e5e5e5;
  border-radius: 8px;
}
.tool-call-item {
  display: flex; gap: 10px; padding: 8px 0;
  border-bottom: 1px solid #f0ebe4;
}
.tool-call-item:last-child { border-bottom: none; }
.tool-icon { font-size: 16px; flex-shrink: 0; margin-top: 2px; }
.tool-info { flex: 1; min-width: 0; }
.tool-name { font-size: 11px; font-weight: 600; font-family: monospace; color: #c75c3a; }
.tool-output {
  font-size: 11px; color: #8a6e55; margin-top: 4px;
  line-height: 1.5; white-space: pre-wrap;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}

/* Connector */
.step-connector {
  position: absolute; left: 25px; top: 42px; bottom: -10px;
  width: 2px; background: #e5e5e5;
}
.step-done .step-connector { background: rgba(90,138,106,0.3); }

/* Result */
.result-section {
  margin-top: 16px; padding: 20px;
  background: #ffffff; border: 1px solid #e5e5e5;
  border-radius: 10px;
}
.result-header { margin-bottom: 12px; }
.result-meta { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.meta-tag {
  font-size: 10px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.5px; color: #6b4f3a;
  padding: 3px 8px; border-radius: 4px; background: #f0ebe4;
}
.meta-time {
  font-size: 11px; color: #8a6e55;
  display: flex; align-items: center; gap: 4px;
}
.result-answer { font-size: 14px; line-height: 1.75; color: #2c1810; }
.result-sources { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.source-tag {
  font-size: 10px; color: #c75c3a;
  padding: 3px 10px; border-radius: 100px;
  background: rgba(199,92,58,0.08);
  border: 1px solid rgba(199,92,58,0.15);
}

/* Loading bar */
.loading-bar {
  margin-top: 12px; height: 3px;
  background: #e5e5e5; border-radius: 2px; overflow: hidden;
}
.loading-bar-inner {
  width: 40%; height: 100%;
  background: linear-gradient(90deg, transparent, #c75c3a, transparent);
  border-radius: 2px;
  animation: shimmer 1.5s infinite;
}

/* Transitions */
.slide-enter-active { transition: all 0.3s cubic-bezier(0.16,1,0.3,1); overflow: hidden; }
.slide-leave-active { transition: all 0.2s ease; overflow: hidden; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; }
.slide-enter-to { max-height: 400px; opacity: 1; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulseRing {
  0% { box-shadow: 0 0 0 0 rgba(199,92,58,0.3); }
  70% { box-shadow: 0 0 0 6px rgba(199,92,58,0); }
  100% { box-shadow: 0 0 0 0 rgba(199,92,58,0); }
}
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(350%); }
}
</style>
