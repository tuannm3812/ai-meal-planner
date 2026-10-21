import { describe, expect, it } from 'vitest'

// The backend's corpus itself, so a suggestion can never drift from the menu.
import corpus from '../../../../data/meal_corpus/meals.json'
import { CRAVING_SUGGESTIONS, requestErrorsFrom422, validateRequest } from './craving'

const VALID = { craving: 'fried rice', location: 'Earlwood, NSW', userId: 'user_123' }

describe('CRAVING_SUGGESTIONS', () => {
  it('names only meals the corpus really has', () => {
    const names = new Set(corpus.map((meal) => meal.name))
    for (const suggestion of CRAVING_SUGGESTIONS) {
      expect(names.has(suggestion.meal), suggestion.meal).toBe(true)
    }
  })
})

describe('validateRequest', () => {
  it('accepts a valid request and an empty craving with no message', () => {
    expect(validateRequest(VALID)).toEqual({})
    expect(validateRequest({ ...VALID, craving: '   ' })).toEqual({})
  })

  it.each([
    ['craving', 'x', 'Use at least 2 characters.'],
    ['craving', 'a'.repeat(181), 'Use at most 180 characters (now 181).'],
    ['location', '', 'Enter a location.'],
    ['location', 'N', 'Use at least 2 characters.'],
    ['location', 'a'.repeat(161), 'Use at most 160 characters (now 161).'],
    ['userId', '', 'Enter a user ID.'],
    ['userId', 'ab', 'Use at least 3 characters.'],
  ])('rejects %s = %j with MealRequest bounds', (key, value, message) => {
    expect(validateRequest({ ...VALID, [key]: value })[key]).toBe(message)
  })

  it('measures the trimmed value, as the request sends it', () => {
    expect(validateRequest({ ...VALID, craving: `  ${'a'.repeat(180)}  ` })).toEqual({})
  })
})

describe('requestErrorsFrom422', () => {
  it('maps craving, location and user_id', () => {
    const detail = [
      { loc: ['body', 'craving'], msg: 'too long' },
      { loc: ['body', 'location'], msg: 'too short' },
      { loc: ['body', 'user_id'], msg: 'bad id' },
      { loc: ['body', 'age'], msg: 'profile, not here' },
    ]
    expect(requestErrorsFrom422(detail)).toEqual({
      craving: 'too long',
      location: 'too short',
      userId: 'bad id',
    })
  })

  it('returns null for a string detail or none of these fields', () => {
    expect(requestErrorsFrom422('nope')).toBeNull()
    expect(requestErrorsFrom422([{ loc: ['body', 'age'], msg: 'x' }])).toBeNull()
  })
})
