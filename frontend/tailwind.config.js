/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyberBg: '#030712',
        cyberPanel: '#0a1628',
        cyberPanelSoft: 'rgba(10, 18, 35, 0.82)',
        cyberCard: 'rgba(12, 22, 42, 0.88)',
        cyberBorder: 'rgba(56, 189, 248, 0.12)',
        cyberBorderGlow: 'rgba(56, 189, 248, 0.35)',
        neonBlue: '#38bdf8',
        neonCyan: '#06b6d4',
        neonGreen: '#10b981',
        neonAmber: '#f59e0b',
        neonRed: '#ef4444',
        neonPurple: '#a855f7',
      },
      boxShadow: {
        'glow-blue': '0 0 24px -4px rgba(56, 189, 248, 0.3), 0 0 6px -1px rgba(56, 189, 248, 0.15)',
        'glow-red': '0 0 24px -4px rgba(239, 68, 68, 0.4), 0 0 6px -1px rgba(239, 68, 68, 0.2)',
        'glow-green': '0 0 24px -4px rgba(16, 185, 129, 0.3), 0 0 6px -1px rgba(16, 185, 129, 0.15)',
        'glow-amber': '0 0 24px -4px rgba(245, 158, 11, 0.3), 0 0 6px -1px rgba(245, 158, 11, 0.15)',
        'glass': '0 8px 40px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.03)',
        'glass-sm': '0 4px 20px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.02)',
        'inner-glow': 'inset 0 1px 0 rgba(255, 255, 255, 0.04), inset 0 0 20px rgba(56, 189, 248, 0.03)',
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        tech: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px)',
        'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E\")",
      },
      backgroundSize: {
        'grid-24': '24px 24px',
      },
      animation: {
        'glow-pulse': 'glow-pulse 3s ease-in-out infinite',
        'scan-line': 'scan-line 4s linear infinite',
        'border-flow': 'border-flow 3s linear infinite',
        'fade-in-up': 'fade-in-up 0.4s ease-out forwards',
        'shimmer': 'shimmer 2.5s ease-in-out infinite',
      },
      keyframes: {
        'glow-pulse': {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        },
        'scan-line': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        'border-flow': {
          '0%': { backgroundPosition: '0% 50%' },
          '100%': { backgroundPosition: '200% 50%' },
        },
        'fade-in-up': {
          'from': { opacity: '0', transform: 'translateY(8px)' },
          'to': { opacity: '1', transform: 'translateY(0)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
