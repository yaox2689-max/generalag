<script setup lang="ts">
import { ref } from 'vue'
import { Terminal, Loader2, Send } from 'lucide-vue-next'

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{ send: [query: string] }>()

const input = ref('')

function handleSend() {
  const q = input.value.trim()
  if (!q || props.disabled) return
  emit('send', q)
  input.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

const hints = [
  '茅台2024年Q3财报分析',
  '计算 2^100',
  '什么是RAG？',
  '对比比亚迪和特斯拉营收',
]
</script>

<template>
  <div class="border-t border-border bg-bg-primary shrink-0">
    <!-- Quick hints -->
    <div class="flex gap-2 px-6 pt-3 overflow-x-auto scrollbar-none">
      <button
        v-for="hint in hints"
        :key="hint"
        @click="!disabled && emit('send', hint)"
        :disabled="disabled"
        class="shrink-0 px-3 py-1.5 text-xs rounded-lg border border-border bg-bg-secondary
               hover:border-accent/40 hover:bg-bg-hover transition-all duration-200
               text-text-secondary hover:text-text-primary cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {{ hint }}
      </button>
    </div>

    <!-- Input -->
    <div class="flex items-center gap-3 px-6 py-4">
      <Terminal :size="18" class="text-accent shrink-0" />
      <div class="flex-1 flex items-center bg-bg-secondary border border-border-light rounded-xl px-4 py-2.5
                  focus-within:border-accent/50 focus-within:shadow-[0_0_16px_rgba(108,92,231,0.12)] transition-all duration-300">
        <span class="text-accent mr-2 text-sm font-mono select-none">&gt;</span>
        <input
          v-model="input"
          @keydown="handleKeydown"
          :disabled="disabled"
          placeholder="Ask anything..."
          class="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-muted outline-none"
        />
        <button
          @click="handleSend"
          :disabled="disabled || !input.trim()"
          class="ml-2 w-8 h-8 rounded-lg flex items-center justify-center
                 transition-all duration-200 cursor-pointer
                 disabled:opacity-30 disabled:cursor-not-allowed
                 enabled:bg-accent enabled:hover:bg-accent-light enabled:active:scale-90"
        >
          <Loader2 v-if="disabled" :size="16" class="text-white animate-spin" />
          <Send v-else :size="16" :class="input.trim() ? 'text-white' : 'text-text-muted'" />
        </button>
      </div>
    </div>
  </div>
</template>
