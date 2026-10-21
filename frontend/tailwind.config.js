/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // "Kitchen green" tokens from docs/8_design.md §4. Components use these
      // names (bg-ink, text-muted, ...) rather than raw hex.
      colors: {
        ink: '#15291F',
        muted: '#4B5B52',
        ground: '#F6F7F2',
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
        protein: '#2F6FAB',
        carbs: '#9A6A12',
        fat: '#7A4E9C',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Bricolage Grotesque"', 'Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
