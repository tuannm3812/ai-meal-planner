import { describe, expect, it } from 'vitest'

import { SAMPLE_PLAN } from './samplePlan'
import { aisles, storeOf, total } from './shopping'

const SHOPPING = SAMPLE_PLAN.shopping_list

describe('aisles', () => {
  it('groups items by aisle in the order the list first reaches each', () => {
    const groups = aisles(SHOPPING)
    expect(groups.map((group) => group.name)).toEqual([
      'Meat & Poultry',
      'Pantry',
      'Grocery',
      'Asian Foods',
    ])
    expect(groups[2].items.map((item) => item.ingredient)).toEqual([
      'whole egg',
      'mixed vegetables',
      'sesame oil',
    ])
  })

  it('marks products and prices the service guessed from a category', () => {
    const items = aisles(SHOPPING).flatMap((group) => group.items)
    expect(items.find((item) => item.ingredient === 'chicken breast').roughEstimate).toBe(false)
    expect(items.find((item) => item.ingredient === 'cooked white rice').roughEstimate).toBe(true)
  })

  it('keeps two items for the same product apart, and files an aisle-less item under Other', () => {
    const groups = aisles({
      shopping_list: [
        { original_item_name: 'a', store_product_name: 'Same', estimated_price: 1 },
        { original_item_name: 'b', store_product_name: 'Same', estimated_price: 2 },
      ],
    })
    expect(groups).toHaveLength(1)
    expect(groups[0].name).toBe('Other')
    expect(groups[0].items.map((item) => item.id)).toEqual([0, 1])
  })

  it('invents no price and returns nothing for a missing list', () => {
    expect(aisles({ shopping_list: [{ original_item_name: 'x' }] })[0].items[0].price).toBeNull()
    expect(aisles(null)).toEqual([])
    expect(aisles({})).toEqual([])
  })
})

describe('storeOf and total', () => {
  it('says whether the store was matched or guessed for the area', () => {
    expect(storeOf(SHOPPING)).toEqual({
      name: 'Coles Supermarket',
      address: 'Earlwood, NSW 2206',
      guessed: false,
    })
    const regional = { store_details: { store_name: 'Woolworths Metro', location_source: 'regional_estimate' } }
    expect(storeOf(regional)).toEqual({ name: 'Woolworths Metro', address: null, guessed: true })
    expect(storeOf({})).toBeNull()
  })

  it("uses the service's total, never a recomputed one", () => {
    expect(total(SHOPPING)).toBe(24.5)
    expect(total({ total_estimated_cost: 'n/a' })).toBeNull()
  })
})
