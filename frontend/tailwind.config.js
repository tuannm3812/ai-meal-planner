/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // "Kitchen green" tokens, Flat kitchen edition (DESIGN.md, DEC-37).
      // Components use these names (bg-ink, text-muted, ...) rather than raw hex.
      colors: {
        ink: '#15291F',
        muted: '#4B5B52',
        ground: '#EEF4EF',
        tint: '#DCEEE1',
        surface: '#FFFFFF',
        line: '#DDE3DA',
        accent: {
          DEFAULT: '#C8431F',
          text: '#B23A17',
        },
        success: {
          bg: '#E3EFE6',
          fg: '#1B5E3F',
        },
        estimate: {
          bg: '#FBEBD6',
          fg: '#7A4A0C',
        },
        // Viridis: macros take three stops, each at least 3:1 on white.
        protein: '#440154',
        carbs: '#2A788E',
        fat: '#22A884',
        // The six-step ramp for categorical series, always with a text label.
        viridis: {
          1: '#440154',
          2: '#414487',
          3: '#2A788E',
          4: '#22A884',
          5: '#7AD151',
          6: '#FDE725',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Bricolage Grotesque"', 'Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
