<template>
  <div class="panel-glass rounded-xl p-3 flex flex-col">
    <!-- 标题 -->
    <div class="flex items-center justify-between pb-1.5 mb-2 border-b border-cyberBorder/60">
      <h2 class="panel-section-title flex items-center gap-1.5">
        <div class="icon-box-cyan">
          <Bot :size="14" />
        </div>
        <span>安全总监智能助手</span>
      </h2>
      <span class="badge-mono bg-cyan-950/60 text-cyan-300 border border-cyan-800/60">
        应急指挥协同
      </span>
    </div>

    <!-- 快捷提问按钮 -->
    <div class="flex flex-wrap gap-1.5 mb-2">
      <button
        v-for="qp in quickPrompts"
        :key="qp.label"
        @click="chatStore.sendMessage(qp.query)"
        class="px-2.5 py-1 rounded-full bg-slate-900/90 border border-slate-700/50 hover:border-cyan-500/80 text-[10px] text-slate-300 hover:text-cyan-300 transition-all duration-300 hover-lift flex items-center gap-1 shadow-sm"
      >
        <MessageCircle :size="11" />
        <span>{{ qp.label }}</span>
      </button>
    </div>

    <!-- 对话历史滚动框 -->
    <div
      ref="chatBoxRef"
      class="bg-cyberPanelSoft rounded-lg p-2.5 border border-cyberBorder/50 h-28 overflow-y-auto space-y-3 text-[10px] mb-2.5 font-sans shadow-inner-glow"
    >
      <div
        v-for="msg in chatStore.messages"
        :key="msg.id"
        class="flex flex-col fade-in-up"
        :class="msg.sender === 'user' ? 'items-end' : 'items-start'"
      >
        <div
          class="inline-block px-3 py-2 max-w-[90%] leading-relaxed shadow-md"
          :class="msg.sender === 'user' ? 'bg-gradient-to-br from-blue-600 to-blue-800 text-white rounded-2xl rounded-tr-sm shadow-glow-blue' : 'bg-slate-900/90 text-slate-200 border border-slate-700/60 rounded-2xl rounded-tl-sm whitespace-pre-line shadow-glass-sm'"
        >
          {{ msg.text }}
        </div>
      </div>

      <!-- 思考中指示器 -->
      <div v-if="chatStore.isThinking" class="text-left fade-in-up">
        <div class="inline-block px-3 py-1.5 rounded-2xl rounded-tl-sm bg-slate-900/80 border border-cyan-800/40 shadow-glass-sm">
          <span class="text-shimmer text-cyan-400 text-[10px] tracking-wide font-medium flex items-center gap-1.5">
            <span class="glow-dot w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            智能决策中枢推理中...
          </span>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="flex gap-2">
      <input
        v-model="inputQuery"
        @keyup.enter="handleSend"
        type="text"
        placeholder="向 FireGuard 提问现场态势与规范..."
        class="flex-1 bg-slate-950/80 border border-slate-700/60 rounded-full px-3 py-1.5 text-[11px] text-white focus:outline-none focus:border-cyan-400 focus:shadow-glow-blue transition-all duration-300"
      />
      <button
        @click="handleSend"
        :disabled="chatStore.isThinking"
        class="px-3.5 py-1.5 bg-gradient-to-r from-neonBlue to-neonCyan hover:from-blue-400 hover:to-cyan-400 text-slate-950 rounded-full text-xs font-bold shadow-glow-blue transition-all duration-300 disabled:opacity-50 disabled:shadow-none transform active:scale-95"
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
  { label: '工友位置？', query: '木工李伟班组撤离到了哪里？' },
  { label: '合规性判定？', query: '当前逃生方案是否符合现场消防安全疏散规范？' },
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
