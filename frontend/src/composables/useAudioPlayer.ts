import { ref } from 'vue';

export function useAudioPlayer() {
  const isPlaying = ref<boolean>(false);
  const activeWorkerId = ref<string | null>(null);

  function playWorkerVoice(workerId: string, audioUrl?: string, scriptText?: string) {
    activeWorkerId.value = workerId;
    isPlaying.value = true;

    if (audioUrl) {
      const audio = new Audio(`${audioUrl}?t=${Date.now()}`);
      audio.onended = () => {
        isPlaying.value = false;
        activeWorkerId.value = null;
      };
      audio.onerror = () => {
        console.warn('本地音频播放失败，转为系统语音合成');
        speakTextFallback(scriptText);
      };
      audio.play().catch(() => {
        speakTextFallback(scriptText);
      });
    } else {
      speakTextFallback(scriptText);
    }
  }

  function speakTextFallback(text?: string) {
    if (!text || !('speechSynthesis' in window)) {
      isPlaying.value = false;
      activeWorkerId.value = null;
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'zh-CN';
    utterance.rate = 1.05;
    utterance.onend = () => {
      isPlaying.value = false;
      activeWorkerId.value = null;
    };
    utterance.onerror = () => {
      isPlaying.value = false;
      activeWorkerId.value = null;
    };
    window.speechSynthesis.speak(utterance);
  }

  return {
    isPlaying,
    activeWorkerId,
    playWorkerVoice,
  };
}
