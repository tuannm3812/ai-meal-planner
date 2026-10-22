import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { cwd } from 'node:process'

import { describe, expect, it } from 'vitest'

import {
  AMDR_PERCENT,
  calories,
  estimatedCount,
  howItWasMade,
  ingredients,
  matchBadge,
  mealTarget,
  servedSplit,
} from './plan'
import { SAMPLE_PLAN } from './samplePlan'

describe('AMDR_PERCENT', () => {
  it('matches backend/app/core/macro_balance.py', () => {
    // The service's own constants, so the bands drawn here cannot drift from
    // the ranges it balances against. Vitest runs from frontend/.
    const macroBalanceSource = readFileSync(
      resolve(cwd(), '../backend/app/core/macro_balance.py'),
      'utf8',
    )
    const line = macroBalanceSource.match(/^AMDR_PERCENT = (\{.*\})$/m)[1]
    const backend = JSON.parse(line.replace(/\(/g, '[').replace(/\)/g, ']'))
    expect(backend).toEqual(AMDR_PERCENT)
  })
})

describe('servedSplit', () => {
  it('computes each share of the macro calories from served nutrition', () => {
    const split = servedSplit(SAMPLE_PLAN.nutrition)
    expect(Math.round(split.protein)).toBe(27)
    expect(Math.round(split.carbs)).toBe(46)
    expect(Math.round(split.fat)).toBe(27)
  })

  it('returns null when a total is missing or there is no energy', () => {
    expect(servedSplit({})).toBeNull()
    expect(servedSplit({ total_protein: 1, total_carbs: 1 })).toBeNull()
    expect(servedSplit({ total_protein: 0, total_carbs: 0, total_fat: 0 })).toBeNull()
    expect(servedSplit(null)).toBeNull()
  })
})

describe('calories and the meal target', () => {
  it('reads the served total and the first stage that reports a target', () => {
    expect(calories(SAMPLE_PLAN)).toEqual({
      total: 629.1,
      target: 625,
      grams: { protein: 42.1, carbs: 71.1, fat: 18.3 },
    })
    const noBalance = { ...SAMPLE_PLAN, macro_balance: null }
    expect(mealTarget(noBalance)).toBe(625)
    const onlyScaling = { ...noBalance, reconciliation: null }
    expect(mealTarget(onlyScaling)).toBe(625)
  })

  it('invents nothing when the response has no totals or target', () => {
    expect(calories({ nutrition: {} })).toBeNull()
    expect(mealTarget({ nutrition: {} })).toBeNull()
  })
})

describe('ingredients', () => {
  it('tags each served ingredient by its verification', () => {
    expect(ingredients(SAMPLE_PLAN).map((item) => [item.name, item.grams, item.tag])).toEqual([
      ['chicken breast', 85, 'Estimated'],
      ['cooked white rice', 200, 'Estimated'],
      ['whole egg', 45, 'Reference'],
      ['mixed vegetables', 105, 'Reference'],
      ['soy sauce', 15, 'Estimated'],
      ['sesame oil', 10, 'Reference'],
    ])
  })

  it('treats a USDA source as verified and an unknown source as an estimate', () => {
    const plan = {
      nutrition: {
        ingredients_macros: [
          { item_name: 'a', base_quantity_grams: 1, data_source: 'usda_fooddata_central' },
          { item_name: 'b', base_quantity_grams: 1, data_source: 'something_new' },
        ],
      },
    }
    expect(ingredients(plan).map((item) => item.tag)).toEqual(['Verified', 'Estimated'])
  })

  it('falls back to the meal definition, untagged, without verified nutrition', () => {
    const plan = { meal_plan: { meal_definition: { ingredients: [{ item_name: 'x', base_quantity_grams: 9 }] } } }
    expect(ingredients(plan)).toEqual([{ name: 'x', grams: 9, tag: null, estimated: false }])
    expect(estimatedCount(plan)).toBeNull()
  })

  it('counts the estimated ingredients', () => {
    expect(estimatedCount(SAMPLE_PLAN)).toEqual({ estimated: 3, of: 6 })
  })
})

describe('matchBadge', () => {
  it('names matched and fallback plans and nothing else', () => {
    expect(matchBadge({ plan_status: 'matched' }).label).toBe('Close menu match')
    expect(matchBadge({ plan_status: 'fallback' }).label).toBe('Standard meal')
    expect(matchBadge({})).toBeNull()
  })
})

describe('howItWasMade', () => {
  it('states the daily estimate, the default workout and the service notes', () => {
    const notes = howItWasMade(SAMPLE_PLAN)
    expect(notes[0]).toBe('Your estimated daily energy is 2,231 kcal; this meal is sized to 625 kcal.')
    expect(notes[1]).toMatch(/default 30-minute workout at 100 bpm/)
    expect(notes).toContain('Matched terms: chicken, fried, rice')
    expect(notes).toContain('Estimated nutrition for soy sauce')
  })

  it('claims no workout when the rule-based fallback made the estimate', () => {
    const plan = {
      ...SAMPLE_PLAN,
      calorie_budget: {
        ...SAMPLE_PLAN.calorie_budget,
        model_version: 'mifflin_st_jeor_fallback_v0.1.0',
      },
    }
    expect(howItWasMade(plan).some((note) => note.includes('workout'))).toBe(false)
  })

  it('is empty for a response with no notes', () => {
    expect(howItWasMade({})).toEqual([])
  })
})
