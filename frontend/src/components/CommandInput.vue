<script setup lang="ts">
import { ref } from 'vue'
import { Loader2, ArrowUp } from 'lucide-vue-next'

const props = defineProps<{ disabled: boolean }>()
const emit = defineEmits<{ send: [query: string] }>()
const input = ref('')

function handleSend() {
  const q = input.value.trim()
  if (!q || props.disabled) return
  emit('send', q)
  input.value = ''
}
</script>

<template>
  <div class="px-5 pb-5 pt-2 shrink-0">
    <div
      class="flex items-center gap-3 bg-warm-700/50 border border-warm-600/60 rounded-2xl px-4 py-3
             focus-within:border-amber-500/40 focus-within:shadow-[0_0_20px_rgba(245,158,11,0.08)]
             transition-all duration-300"
    >
      <input
        v-model="input"
        @keydown.enter.prevent="handleSend"
        :disabled="disabled"
        placeholder="Ask anything..."
        class="flex-1 bg-transparent text-sm text-warm-100 placeholder:text-warm-500 outline-none"
      />
      <button
        @click="handleSend"
        :disabled="disabled || !input.trim()"
        class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0
               transition-all duration-200 cursor-pointer
               disabled:opacity-30 disabled:cursor-not-allowed
               enabled:bg-amber-500 enabled:hover:bg-amber-400 enabled:active:scale-90
               shadow-[0_2px_8px_rgba(245,158,11,0.25)]"
      >
        <Loader2 v-if="disabled" :size="15" class="text-warm-900 animate-spin" />
        <ArrowUp v-else :size="15" :class="input.trim() ? 'text-warm-900' : 'text-warm-500'" />
      </button>
    </div>
    <p class="text-center text-[10px] text-warm-500/60 mt-2.5">
      General Agent v0.1 &mdash; Self-built Plan-and-Execute Engine
    </p>
  </div>
</template>
