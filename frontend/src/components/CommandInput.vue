<script setup lang="ts">
import { ref } from 'vue'
import { ArrowUp, Loader2 } from 'lucide-vue-next'

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{ send: [query: string] }>()
const input = ref('')
const focused = ref(false)

function handleSend() {
  const q = input.value.trim()
  if (!q || props.disabled) return
  emit('send', q)
  input.value = ''
}
</script>

<template>
  <div class="shrink-0 pt-3 pb-1 animate-fade-in-up" style="animation-delay: 0.15s">
    <div
      class="flex items-center gap-3 rounded-2xl border-2 px-4 py-3 transition-all duration-300"
      :class="focused
        ? 'bg-white border-terracotta/40 shadow-lg shadow-terracotta/8'
        : 'bg-white/70 border-parchment hover:border-sand-light'"
    >
      <input
        v-model="input"
        @keydown.enter.prevent="handleSend"
        @focus="focused = true"
        @blur="focused = false"
        :disabled="disabled"
        placeholder="Ask anything..."
        class="flex-1 bg-transparent text-sm text-espresso placeholder:text-sand outline-none"
      />
      <button
        @click="handleSend"
        :disabled="disabled || !input.trim()"
        class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0
               transition-all duration-200 cursor-pointer
               disabled:opacity-30 disabled:cursor-not-allowed
               enabled:bg-terracotta enabled:hover:bg-terracotta-light enabled:active:scale-90
               shadow-md shadow-terracotta/20"
      >
        <Loader2 v-if="disabled" :size="16" class="text-white animate-spin" />
        <ArrowUp v-else :size="16" :class="input.trim() ? 'text-white' : 'text-sand'" />
      </button>
    </div>
    <p class="text-center text-[10px] text-sand mt-2">
      General Agent v0.1 &mdash; Self-built Plan-and-Execute Engine
    </p>
  </div>
</template>
