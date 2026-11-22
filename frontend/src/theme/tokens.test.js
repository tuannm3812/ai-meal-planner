import { describe, expect, it } from 'vitest'

import tailwindConfig from '../../tailwind.config.js'
import { brand, food, MACRO_COLORS, neutral, status, VIRIDIS } from './tokens'

// The palette guard (DESIGN.md §3 and §5, DEC-38). Every source file is read
// as text, so a stray colour or icon fails here rather than in review.
const sources = import.meta.glob(['/src/**/*.{js,jsx,css}', '!/src/**/*.test.{js,jsx}', '!/src/test/**'], {
  eager: true,
  import: 'default',
  query: '?raw',
})
const files = Object.entries(sources).map(([path, text]) => [path.replace(/^\/src\//, ''), text])

const offenders = (pattern, allowed = () => false) =>
  files.filter(([path, text]) => !allowed(path) && pattern.test(text)).map(([path]) => path)

const STOCK =
  /\b(?:bg|text|border|ring|fill|stroke|from|to|via|divide|outline|placeholder|decoration|shadow|caret)-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}\b/

describe('palette guard', () => {
  it('reads the source files', () => {
    expect(files.length).toBeGreaterThan(40)
  })

  it('keeps raw hex colours in the tokens file only', () => {
    expect(offenders(/#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b(?![\w-])/, (p) => p === 'theme/tokens.js')).toEqual([])
  })

  it("uses no Tailwind stock colours, only the app's tokens", () => {
    expect(offenders(STOCK)).toEqual([])
  })

  it('keeps macro colours on macro data in the plan feature', () => {
    expect(
      offenders(/\b(?:bg|text|ring|border|fill|stroke)-(?:protein|carbs|fat)\b/, (p) => p.startsWith('features/plan/')),
    ).toEqual([])
  })

  it('imports Lucide only through the Icon folder', () => {
    expect(offenders(/from ['"]lucide-react['"]/, (p) => p.startsWith('components/icons/'))).toEqual([])
  })

  it('sizes icons through Icon, never by hand', () => {
    expect(offenders(/strokeWidth=\{1\.[0-9]+\}|\bsize=\{\d+\}/, (p) => p.startsWith('components/icons/'))).toEqual([])
  })
})

describe('tokens', () => {
  const all = { ...neutral, ...brand, ...status, ...food }

  it('are all six-digit hex values', () => {
    for (const value of [...Object.values(all), ...VIRIDIS]) expect(value).toMatch(/^#[0-9A-F]{6}$/)
  })

  it('give the macros three Viridis stops', () => {
    expect(MACRO_COLORS).toEqual({ protein: VIRIDIS[0], carbs: VIRIDIS[2], fat: VIRIDIS[3] })
  })

  it('are what Tailwind maps its class names to', () => {
    const colors = tailwindConfig.theme.extend.colors
    expect(colors.ink.DEFAULT).toBe(neutral.ink)
    expect(colors.leaf).toBe(brand.leaf)
    expect(colors.danger.fg).toBe(status.dangerFg)
    expect(colors.viridis[6]).toBe(VIRIDIS[5])
  })
})
