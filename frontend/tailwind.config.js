import { brand, data, MACRO_COLORS, neutral, status, VIRIDIS } from './src/theme/tokens.js'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      // Every colour comes from src/theme/tokens.js (DESIGN.md §3, DEC-38).
      // Components use these names (bg-ink, text-cobalt, ...), never raw hex
      // or Tailwind's stock palette.
      colors: {
        ink: { DEFAULT: neutral.ink, raised: neutral.inkRaised },
        muted: neutral.muted,
        'on-ink-muted': neutral.onInkMuted,
        line: neutral.line,
        ground: neutral.ground,
        tint: neutral.tint,
        surface: neutral.surface,
        accent: { DEFAULT: brand.coral, text: brand.coralText },
        cobalt: { DEFAULT: brand.cobalt, raised: brand.cobaltRaised },
        peach: brand.peach,
        success: { bg: status.successBg, fg: status.successFg },
        estimate: { bg: status.estimateBg, fg: status.estimateFg },
        danger: { bg: status.dangerBg, fg: status.dangerFg, 'on-ink': status.dangerOnInk },
        protein: MACRO_COLORS.protein,
        carbs: MACRO_COLORS.carbs,
        fat: MACRO_COLORS.fat,
        band: data.band,
        viridis: Object.fromEntries(VIRIDIS.map((hex, index) => [index + 1, hex])),
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Unbounded', 'Inter', 'system-ui', 'sans-serif'],
      },
      // The sticker shadow on primary buttons and outlined cards (DESIGN.md §6).
      boxShadow: {
        sticker: `3px 3px 0 ${neutral.ink}`,
      },
    },
  },
  plugins: [],
}
