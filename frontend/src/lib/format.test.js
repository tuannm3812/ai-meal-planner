import { describe, expect, it } from 'vitest'

import { formatCurrency, formatDateTime, formatMacro, macroCards, parseCommaList } from './format'

describe('formatCurrency', () => {
  it('formats a number as AUD', () => {
    expect(formatCurrency(12.5)).toContain('12.50')
  })

  it('treats null and undefined as zero rather than NaN', () => {
    expect(formatCurrency(null)).toContain('0.00')
    expect(formatCurrency(undefined)).toContain('0.00')
  })
})

describe('formatMacro', () => {
  it('fixes to one decimal and appends the unit', () => {
    expect(formatMacro(31.456, 'g')).toBe('31.5g')
  })

  it('treats a missing value as zero', () => {
    expect(formatMacro(null, ' kcal')).toBe('0.0 kcal')
  })
})

describe('formatDateTime', () => {
  it('returns a placeholder for an empty value', () => {
    expect(formatDateTime('')).toBe('Unknown time')
  })

  it('returns the input unchanged when it is not a date', () => {
    expect(formatDateTime('not-a-date')).toBe('not-a-date')
  })

  it('formats a real ISO timestamp', () => {
    expect(formatDateTime('2026-09-14T10:30:00Z')).not.toBe('Unknown time')
  })
})

describe('parseCommaList', () => {
  it('splits, trims and drops blanks', () => {
    expect(parseCommaList(' a , , b ')).toEqual(['a', 'b'])
  })

  it('returns an empty array for an empty string', () => {
    expect(parseCommaList('')).toEqual([])
  })
})

describe('macroCards', () => {
  it('describes the four macros the nutrition panel renders', () => {
    expect(macroCards.map((card) => card.key)).toEqual([
      'total_calories',
      'total_protein',
      'total_carbs',
      'total_fat',
    ])
  })
})
