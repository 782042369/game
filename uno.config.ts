import {
  defineConfig,
  presetAttributify,
  presetWind4,
  transformerDirectives,
  transformerVariantGroup,
} from 'unocss'

export default defineConfig({
  presets: [
    presetWind4(),
    presetAttributify(),
  ],
  transformers: [transformerDirectives(), transformerVariantGroup()],

  theme: {
    colors: {
      mc: {
        bg: '#313131',
        panel: '#c6c6c6',
        btn: '#c6c6c6',
        border: '#555555',
        light: '#ffffff',
        text: '#1e1e1e',
        exp: '#80ff20',
      },
      safe: '#55ff55',
      warning: '#ffff55',
      danger: '#ff5555',
    },
    fontFamily: {
      pixel: ['"Press Start 2P"', 'cursive'],
      body: ['"VT323"', 'monospace'],
      mono: ['"JetBrains Mono"', 'monospace'],
      sans: ['Inter', 'system-ui', 'sans-serif'],
    },
    animation: {
      'float-up': 'float-up 0.8s ease-out forwards',
      'screen-shake': 'screen-shake 0.2s ease-in-out',
      'glitch': 'glitch 0.3s cubic-bezier(.25,.46,.45,.94) infinite',
      'fade-in-up': 'fade-in-up 0.3s ease-out forwards',
    },
    keyframes: {
      'fade-in-up': {
        '0%': { transform: 'translateY(10px)', opacity: '0' },
        '100%': { transform: 'translateY(0)', opacity: '1' },
      },
      'float-up': {
        '0%': { transform: 'translateY(0)', opacity: '0' },
        '20%': { opacity: '1' },
        '100%': { transform: 'translateY(-40px)', opacity: '0' },
      },
      'screen-shake': {
        '0%, 100%': { transform: 'translateX(0)' },
        '25%': { transform: 'translateX(-4px) translateY(2px)' },
        '50%': { transform: 'translateX(4px) translateY(-2px)' },
        '75%': { transform: 'translateX(-2px) translateY(1px)' },
      },
      'glitch': {
        '0%': { transform: 'translate(0)' },
        '20%': { transform: 'translate(-2px, 2px)' },
        '40%': { transform: 'translate(-2px, -2px)' },
        '60%': { transform: 'translate(2px, 2px)' },
        '80%': { transform: 'translate(2px, -2px)' },
        '100%': { transform: 'translate(0)' },
      },
    },
  },

  shortcuts: {
    'mc-panel': 'bg-mc-panel border-4 border-t-mc-light border-l-mc-light border-b-mc-border border-r-mc-border p-3 shadow-[6px_6px_0px_0px_rgba(0,0,0,0.4)]',
    'mc-btn': 'bg-mc-btn border-2 border-t-mc-light border-l-mc-light border-b-mc-border border-r-mc-border px-4 py-2 text-mc-text font-pixel font-bold hover:bg-[#d5d5d5] hover:shadow-[inset_0_0_10px_rgba(255,255,255,0.4)] active:border-t-mc-border active:border-l-mc-border active:border-b-mc-light active:border-r-mc-light outline-none select-none transition-all duration-75',
    'mc-bar-bg': 'bg-[#000000] border-2 border-[#555555] h-6 relative shadow-[inset_2px_2px_4px_rgba(0,0,0,0.5)]',
    'pixel-glow-text': 'text-shadow-glow',
  },

  rules: [
    ['pixel-cursor', { cursor: 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'16\' height=\'16\'%3E%3Ctext y=\'14\' font-size=\'12\' fill=\'%23ffffff\'%3E▮%3C/text%3E%3C/svg%3E") 0 0, auto' }],
    ['text-shadow-glow', { 'text-shadow': '3px 3px 0px rgba(0,0,0,0.6)' }],
    ['mc-text-shadow', { 'text-shadow': '1px 1px 0px rgba(255,255,255,0.3)' }],
  ],
})
