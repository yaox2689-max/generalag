<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Send, Loader2 } from 'lucide-vue-next'

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{ send: [query: string] }>()

const input = ref('')
const textarea = ref<HTMLTextAreaElement>()

function handleSend() {
  const query = input.value.trim()
  if (!query || props.disabled) return
  emit('send', query)
  input.value = ''
  adjustHeight()
}

function adjustHeight() {
  if (!textarea.value) return
  textarea.value.style.height = 'auto'
  textarea.value.style.height = Math.min(textarea.value.scrollHeight, 150) + 'px'
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

onMounted(() => {
  textarea.value?.focus()
})
</script>

<template>
  <div class="px-6 pb-6 pt-2 shrink-0">
    <div
      class="flex items-end gap-3 bg-bg-secondary border border-border-light rounded-2xl px-4 py-3
             focus-within:border-accent/50 focus-within:shadow-[0_0_20px_rgba(108,92,231,0.15)]
             transition-all duration-300"
    >
      <textarea
        ref="textarea"
        v-model="input"
        @keydown="handleKeydown"
        @input="adjustHeight"
        :disabled="disabled"
        placeholder="Ask me anything... (Shift+Enter for new line)"
        rows="1"
        class="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-muted
               resize-none outline-none min-h-[24px] max-h-[150px] leading-relaxed"
      />
      <button
        @click="handleSend"
        :disabled="disabled || !input.trim()"
        class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0
               transition-all duration-200 cursor-pointer
               disabled:opacity-30 disabled:cursor-not-allowed
               enabled:bg-accent enabled:hover:bg-accent-light enabled:active:scale-95"
      >
        <Loader2 v-if="disabled" :size="18" class="text-white animate-spin" />
        <Send v-else :size="18" :class="input.trim() ? 'text-white' : 'text-text-muted'" />
      </button>
    </div>
    <p class="text-center text-xs text-text-muted mt-2">
      General Agent v0.1 — Built with a self-built agent engine
    </p>
  </div>
</template>
