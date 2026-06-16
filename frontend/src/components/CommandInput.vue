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
  <div class="command-input-wrap">
    <div class="command-input-bar" :class="{ focused }">
      <input
        v-model="input"
        @keydown.enter.prevent="handleSend"
        @focus="focused = true"
        @blur="focused = false"
        :disabled="disabled"
        placeholder="Ask anything..."
        class="command-input"
      />
      <button
        @click="handleSend"
        :disabled="disabled || !input.trim()"
        class="send-btn"
      >
        <Loader2 v-if="disabled" :size="16" class="text-white animate-spin" />
        <ArrowUp v-else :size="16" :class="input.trim() ? 'text-white' : 'text-sand'" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.command-input-wrap {
  width: 100%;
}

.command-input-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  border: 1.5px solid #e5e5e5;
  border-radius: 12px;
  padding: 10px 16px;
  transition: all 0.25s ease;
}

.command-input-bar.focused {
  border-color: rgba(199, 92, 58, 0.4);
  box-shadow: 0 0 0 3px rgba(199, 92, 58, 0.08);
}

.command-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: #2c1810;
  font-family: inherit;
}

.command-input::placeholder {
  color: #b8a898;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  cursor: pointer;
  border: none;
  background: #e5e5e5;
  color: #b8a898;
  transition: all 0.2s ease;
}

.send-btn:not(:disabled) {
  background: #c75c3a;
  box-shadow: 0 2px 8px rgba(199, 92, 58, 0.25);
}

.send-btn:not(:disabled):hover {
  background: #e8825f;
}

.send-btn:not(:disabled):active {
  transform: scale(0.92);
}

.send-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
</style>
