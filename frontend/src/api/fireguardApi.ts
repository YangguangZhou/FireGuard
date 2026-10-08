import type { ActType, EmergencyStateResponse } from '@/types/emergency';

export const fireguardApi = {
  async getState(): Promise<EmergencyStateResponse> {
    const res = await fetch('/api/state');
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  },

  async triggerAct(actKey: ActType): Promise<any> {
    const res = await fetch('/api/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ act_key: actKey }),
    });
    if (!res.ok) throw new Error(`Trigger failed: ${res.status}`);
    return await res.json();
  },

  async askCopilot(question: string): Promise<string> {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    if (!res.ok) throw new Error(`Chat error: ${res.status}`);
    const data = await res.json();
    return data.answer || '系统未返回有效回复';
  },

  async getFormalReport(): Promise<any> {
    const res = await fetch('/api/report');
    if (!res.ok) throw new Error(`Report fetch failed: ${res.status}`);
    return await res.json();
  },
};
