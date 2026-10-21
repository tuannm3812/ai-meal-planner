import { describe, expect, it } from 'vitest'

import {
  AVOID_OPTIONS,
  DEFAULT_PROFILE,
  profileErrorsFrom422,
  profileToRequest,
  sameRequest,
  validateProfile,
} from './profile'

describe('profileToRequest', () => {
  it('sends numbers and the MealRequest field names', () => {
    expect(profileToRequest(DEFAULT_PROFILE)).toEqual({
      goal: 'maintain',
      age: 34,
      sex: 'female',
      height_cm: 168,
      weight_kg: 64,
      activity_multiplier: 1.55,
      dietary_preferences: [],
      health_conditions: [],
    })
  })

  it('maps each avoid-chip onto the field and value docs/8_design.md §3.1 names', () => {
    const all = { ...DEFAULT_PROFILE, avoid: AVOID_OPTIONS.map((option) => option.id) }
    const request = profileToRequest(all)
    expect(request.dietary_preferences).toEqual([
      'vegetarian',
      'vegan',
      'dairy-free',
      'gluten-free',
    ])
    expect(request.health_conditions).toEqual(['peanut allergy', 'kidney disease'])
  })

  it('offers no avoid-option the rules do not enforce', () => {
    const labels = AVOID_OPTIONS.map((option) => option.label.toLowerCase())
    expect(labels.some((label) => label.includes('diabet'))).toBe(false)
  })
})

describe('validateProfile', () => {
  it('accepts the defaults', () => {
    expect(validateProfile(DEFAULT_PROFILE)).toEqual({})
  })

  it.each([
    ['age', '', 'Enter your age.'],
    ['age', '0', 'Age must be more than 0 and at most 120 years.'],
    ['age', '121', 'Age must be more than 0 and at most 120 years.'],
    ['age', '34.5', 'Age must be a whole number.'],
    ['heightCm', '80', 'Height must be more than 80 and at most 260 cm.'],
    ['weightKg', '351', 'Weight must be more than 20 and at most 350 kg.'],
    ['weightKg', 'abc', 'Weight must be a number.'],
  ])('rejects %s = %j with the service bounds', (key, value, message) => {
    expect(validateProfile({ ...DEFAULT_PROFILE, [key]: value })[key]).toBe(message)
  })

  it('accepts the bounds the service accepts', () => {
    const edge = { ...DEFAULT_PROFILE, age: '120', heightCm: '260', weightKg: '20.5' }
    expect(validateProfile(edge)).toEqual({})
  })

  it('rejects a goal, sex or activity outside the offered options', () => {
    const errors = validateProfile({ ...DEFAULT_PROFILE, goal: 'x', sex: '', activity: '3' })
    expect(Object.keys(errors).sort()).toEqual(['activity', 'goal', 'sex'])
  })
})

describe('sameRequest', () => {
  it('ignores edits that send the same request', () => {
    const retyped = { ...DEFAULT_PROFILE, weightKg: '64.0' }
    expect(sameRequest(DEFAULT_PROFILE, retyped)).toBe(true)
  })

  it('sees a changed value or chip', () => {
    expect(sameRequest(DEFAULT_PROFILE, { ...DEFAULT_PROFILE, goal: 'lose' })).toBe(false)
    expect(sameRequest(DEFAULT_PROFILE, { ...DEFAULT_PROFILE, avoid: ['vegan'] })).toBe(false)
  })
})

describe('profileErrorsFrom422', () => {
  it('maps request fields back to profile keys', () => {
    const detail = [
      { loc: ['body', 'age'], msg: 'Input should be less than or equal to 120' },
      { loc: ['body', 'height_cm'], msg: 'Input should be greater than 80' },
    ]
    expect(profileErrorsFrom422(detail)).toEqual({
      age: 'Input should be less than or equal to 120',
      heightCm: 'Input should be greater than 80',
    })
  })

  it('returns null for a string detail or one naming no profile field', () => {
    expect(profileErrorsFrom422('Backend exploded')).toBeNull()
    expect(profileErrorsFrom422([{ loc: ['body', 'craving'], msg: 'too short' }])).toBeNull()
  })
})
