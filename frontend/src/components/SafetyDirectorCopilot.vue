<template>
  <div class="bg-cyberPanelSoft border border-cyberBorder rounded-xl p-3 flex flex-col shadow-glass">
    <!-- 标题 -->
    <div class="flex items-center justify-between pb-1.5 mb-2 border-b border-cyberBorder/60">
      <h2 class="text-xs font-bold text-slate-100 flex items-center gap-1.5">
        <Bot :size="14" />
        <span>安全总监 Copilot (qwen-plus / qwen3.7-plus)</span>
      </h2>
      <span class="text-[9px] px-1.5 py-0.5 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-800/60">
        GB/T 50720 规则推理
      </span>
    </div>

    <!-- 快捷提问按钮 -->
    <div class="flex flex-wrap gap-1.5 mb-2">
      <button
        v-for="qp in quickPrompts"
        :key="qp.label"
        @click="chatStore.sendMessage(qp.query)"
        class="px-2 py-0.5 rounded bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/50 text-[10px] text-slate-400 hover:text-cyan-300 transition"
      >
        <MessageCircle class="inline-block mr-1" :size="11" />{{ qp.label }}
      </button>
    </div>

    <!-- 对话历史滚动框 -->
    <div
      ref="chatBoxRef"
      class="bg-slate-950/80 rounded-lg p-2 border border-slate-900 h-28 overflow-y-auto space-y-2 text-[10px] mb-2 font-sans"
    >
      <div
        v-for="msg in chatStore.messages"
        :key="msg.id"
        :class="msg.sender === 'user' ? 'text-right' : 'text-left'"
      >
        <span
          class="inline-block px-2.5 py-1.5 rounded-lg max-w-[92%] leading-relaxed shadow-sm"
          :class="msg.sender === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-slate-900 text-slate-200 border border-slate-800 rounded-bl-none whitespace-pre-line'"
        >
          {{ msg.text }}
        </span>
      </div>

      <!-- 思考中指示器 -->
      <div v-if="chatStore.isThinking" class="text-left">
        <span class="inline-block px-2 py-1 rounded bg-slate-900 border border-slate-800 text-cyan-400 text-[10px] animate-pulse">
          通义模型推理中...
        </span>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="flex gap-1.5">
      <input
        v-model="inputQuery"
        @keyup.enter="handleSend"
        type="text"
        placeholder="向 FireGuard 提问现场态势与规范..."
        class="flex-1 bg-slate-950/90 border border-slate-800 rounded-lg px-2.5 py-1.5 text-[11px] text-white focus:outline-none focus:border-cyan-400 transition"
      />
      <button
        @click="handleSend"
        :disabled="chatStore.isThinking"
        class="px-3 py-1.5 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white rounded-lg text-xs font-semibold shadow transition disabled:opacity-50"
      >
        发送
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { Bot, MessageCircle } from 'lucide-vue-next';
import { useChatStore } from '@/stores/chatStore';

const chatStore = useChatStore();
const inputQuery = ref('');
const chatBoxRef = ref<HTMLElement | null>(null);

const quickPrompts = [
  { label: '哪个出口安全？', query: '当前哪个出口最安全，依据什么规范？' },
  { label: '工友位置？', query: '木工李强班组撤离到了哪里？' },
  { label: '合规性判定？', query: '当前方案是否符合GB/T 50720施工消防技术规范？' },
];

function handleSend() {
  if (!inputQuery.value.trim()) return;
  chatStore.sendMessage(inputQuery.value);
  inputQuery.value = '';
}

watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick();
    if (chatBoxRef.value) {
      chatBoxRef.value.scrollTop = chatBoxRef.value.scrollHeight;
    }
  }
);
</script>
