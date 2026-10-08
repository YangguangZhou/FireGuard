import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fireguardApi } from '@/api/fireguardApi';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'copilot';
  text: string;
  timestamp: string;
}

export const useChatStore = defineStore('chat', () => {
  const isThinking = ref<boolean>(false);
  const messages = ref<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'copilot',
      text: '安全总监您好！我是筑安·火眼应急指挥 Copilot（由通义 Qwen 大模型驱动）。现场全作业面处于受控状态，随时为您解读 GB/T 50720 规范与分流策略。',
      timestamp: new Date().toLocaleTimeString('zh-CN', { hour12: false }),
    },
  ]);

  async function sendMessage(question: string) {
    if (!question.trim() || isThinking.value) return;

    const time = new Date().toLocaleTimeString('zh-CN', { hour12: false });
    messages.value.push({
      id: `u-${Date.now()}`,
      sender: 'user',
      text: question.trim(),
      timestamp: time,
    });

    isThinking.value = true;
    try {
      const answer = await fireguardApi.askCopilot(question);
      messages.value.push({
        id: `c-${Date.now()}`,
        sender: 'copilot',
        text: answer,
        timestamp: new Date().toLocaleTimeString('zh-CN', { hour12: false }),
      });
    } catch (err: any) {
      messages.value.push({
        id: `err-${Date.now()}`,
        sender: 'copilot',
        text: '通义智能中枢通信连接稍慢，请稍后重试。',
        timestamp: new Date().toLocaleTimeString('zh-CN', { hour12: false }),
      });
    } finally {
      isThinking.value = false;
    }
  }

  return {
    isThinking,
    messages,
    sendMessage,
  };
});
