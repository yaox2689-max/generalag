<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { sendQuery } from '../api/agent'
import type { ChatMessage, AgentStep } from '../types'
import ChatMessageComp from '../components/ChatMessage.vue'
import AgentSteps from '../components/AgentSteps.vue'
import InputBox from '../components/InputBox.vue'
import { Bot, Sparkles } from 'lucide-vue-next'

const messages = ref<ChatMessage[]>([])
const currentSteps = ref<AgentStep[]>([])
const isProcessing = ref(false)
const chatContainer = ref<HTMLElement>()

const stepNames = ['Router', 'Planner', 'Executor', 'Verifier', 'Writer']

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7)
}

async function simulateSteps(complexity: string): Promise<void> {
  const steps: AgentStep[] = stepNames.map(name => ({ name, status: 'pending' }))
  currentSteps.value = steps

  const activeSteps = complexity === 'simple'
    ? ['Router', 'Executor', 'Writer']
    : stepNames

  for (const stepName of activeSteps) {
    const step = steps.find(s => s.name === stepName)!
    step.status = 'running'
    currentSteps.value = [...steps]
    await new Promise(r => setTimeout(r, 400 + Math.random() * 300))
    step.status = 'done'
    currentSteps.value = [...steps]
  }
}

async function handleSend(query: string) {
  const userMsg: ChatMessage = {
    id: generateId(),
    role: 'user',
    content: query,
    timestamp: Date.now(),
  }
  messages.value.push(userMsg)

  const aiMsg: ChatMessage = {
    id: generateId(),
    role: 'assistant',
    content: '',
    timestamp: Date.now(),
    loading: true,
  }
  messages.value.push(aiMsg)
  isProcessing.value = true
  scrollToBottom()

  try {
    const response = await sendQuery(query)
    aiMsg.agentResponse = response
    await simulateSteps(response.complexity)

    // Simulate typewriter effect
    const fullText = response.answer
    aiMsg.content = ''
    for (let i = 0; i < fullText.length; i++) {
      aiMsg.content += fullText[i]
      if (i % 3 === 0) {
        await new Promise(r => setTimeout(r, 15))
        scrollToBottom()
      }
    }
    aiMsg.content = fullText
    aiMsg.loading = false
  } catch (err: any) {
    aiMsg.content = `Error: ${err.message || 'Failed to reach agent'}. Make sure the backend is running on port 8000.`
    aiMsg.loading = false
    currentSteps.value = []
  } finally {
    isProcessing.value = false
    scrollToBottom()
  }
}

watch(messages, scrollToBottom, { deep: true })
</script>

<template>
  <div class="flex flex-col h-full max-w-4xl mx-auto w-full">
    <!-- Header -->
    <header class="flex items-center gap-3 px-6 py-4 border-b border-border shrink-0">
      <div class="w-9 h-9 rounded-xl bg-accent/20 flex items-center justify-center">
        <Bot :size="20" class="text-accent-light" />
      </div>
      <div>
        <h1 class="text-base font-semibold text-text-primary leading-tight">General Agent</h1>
        <p class="text-xs text-text-muted">Pluggable Agent Framework</p>
      </div>
      <div class="ml-auto flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-success animate-pulse"></div>
        <span class="text-xs text-text-secondary">Online</span>
      </div>
    </header>

    <!-- Messages -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto px-6 py-6 space-y-6">
      <!-- Empty state -->
      <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full gap-4 animate-fade-in-up">
        <div class="w-16 h-16 rounded-2xl bg-accent/10 flex items-center justify-center">
          <Sparkles :size="32" class="text-accent-light" />
        </div>
        <h2 class="text-xl font-semibold text-text-primary">What can I help with?</h2>
        <p class="text-sm text-text-secondary max-w-md text-center">
          I'm a general-purpose agent with pluggable tools. Try asking about finance, math, or search.
        </p>
        <div class="flex flex-wrap gap-2 mt-4 justify-center">
          <button
            v-for="hint in ['茅台2024年Q3财报', '计算 2^100', '什么是RAG技术？', '对比比亚迪和特斯拉营收']"
            :key="hint"
            @click="handleSend(hint)"
            class="px-4 py-2 text-sm rounded-xl border border-border-light bg-bg-secondary
                   hover:bg-bg-hover hover:border-accent/30 transition-all duration-200
                   text-text-secondary hover:text-text-primary cursor-pointer"
          >
            {{ hint }}
          </button>
        </div>
      </div>

      <!-- Chat messages -->
      <template v-for="msg in messages" :key="msg.id">
        <ChatMessageComp :message="msg" />
      </template>

      <!-- Agent steps -->
      <AgentSteps v-if="currentSteps.length > 0 && isProcessing" :steps="currentSteps" />
    </div>

    <!-- Input -->
    <InputBox :disabled="isProcessing" @send="handleSend" />
  </div>
</template>
