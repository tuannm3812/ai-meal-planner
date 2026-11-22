import { describe, expect, it } from 'vitest'

import { DISH_TYPES, dishType } from './dishType'

describe('dishType', () => {
  it.each([
    ['Chicken Fried Rice', 'rice'],
    ['Cashew Chicken Stir Fry', 'stirfry'],
    ['Pork Stir Fry Noodles', 'noodles'],
    ['Lentil Bolognese Pasta', 'pasta'],
    ['Turkey Chili Bowl', 'curry'],
    ['Chickpea Curry Bowl', 'curry'],
    ['Chicken Pumpkin Soup', 'soup'],
    ['Tofu Mushroom Noodle Soup', 'soup'],
    ['Beef Taco Salad', 'taco'],
    ['Chickpea Hummus Wrap', 'taco'],
    ['Steak Salad Bowl', 'salad'],
    ['Mushroom Egg Toast', 'eggs'],
    ['Vegetarian Spinach Omelette', 'eggs'],
    ['Vegan Oat Bowl', 'oats'],
    ['Almond Banana Overnight Oats', 'oats'],
    ['Lemon Cod Potato Traybake', 'plate'],
    ['Salmon Quinoa Plate', 'plate'],
    ['Greek Chicken Bowl', 'bowl'],
    ['', 'bowl'],
    [undefined, 'bowl'],
  ])('%s is drawn as %s', (name, expected) => {
    expect(dishType(name)).toBe(expected)
  })

  it('only ever returns a type that has a drawing', () => {
    for (const name of ['Tuna Sushi Bowl', 'Beef Potato Hash', 'Pork Burrito Bowl']) {
      expect(DISH_TYPES).toContain(dishType(name))
    }
  })
})
