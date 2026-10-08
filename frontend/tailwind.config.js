/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyberBg: '#050914',
        cyberPanel: '#0b1325',
        cyberPanelSoft: 'rgba(11, 19, 37, 0.75)',
        cyberCard: 'rgba(15, 23, 42, 0.85)',
        cyberBorder: 'rgba(30, 58, 138, 0.35)',
        cyberBorderGlow: 'rgba(56, 189, 248, 0.4)',
        neonBlue: '#38bdf8',
        neonCyan: '#06b6d4',
        neonGreen: '#10b981',
        neonAmber: '#f59e0b',
        neonRed: '#ef4444',
        neonPurple: '#a855f7',
      },
      boxShadow: {
        'glow-blue': '0 0 20px -3px rgba(56, 189, 248, 0.35)',
        'glow-red': '0 0 20px -3px rgba(239, 68, 68, 0.45)',
        'glow-green': '0 0 20px -3px rgba(16, 185, 129, 0.35)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.45)',
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        tech: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
