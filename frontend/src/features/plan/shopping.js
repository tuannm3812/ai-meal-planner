// The shopping list of docs/8_design.md §3.3, read from a SupermarketPayload
// (backend/app/agents/supermarket_agent.py). Nothing is recomputed: the total
// is the service's, and every price is the service's estimate.

const isNumber = (value) => typeof value === 'number' && Number.isFinite(value)

// The store is a known one only when the service matched the location in its
// reference list; otherwise it named a likely chain for the area.
export function storeOf(shopping) {
  const store = shopping?.store_details
  if (!store?.store_name) return null
  return {
    name: store.store_name,
    address: store.address || null,
    guessed: store.location_source !== 'local_reference',
  }
}

// Plans stored before 2026-11-24 named an unknown product "Generic <ingredient>";
// show the ingredient's name instead, as the service does now.
function productName(name) {
  const plain = String(name ?? '').replace(/^Generic /, '')
  return plain.slice(0, 1).toUpperCase() + plain.slice(1)
}

// Items grouped by aisle, aisles in the order the list first reaches them, so
// the list reads in the service's order. Each item keeps its position as its
// id, since two ingredients can map to the same product.
export function aisles(shopping) {
  const items = shopping?.shopping_list
  if (!Array.isArray(items)) return []
  const groups = new Map()
  items.forEach((item, index) => {
    const aisle = item.category_or_aisle || 'Other'
    if (!groups.has(aisle)) groups.set(aisle, [])
    const product = productName(item.store_product_name || item.original_item_name)
    groups.get(aisle).push({
      id: index,
      product,
      ingredient: item.original_item_name,
      // False when the product is just the ingredient's own name.
      named: product.toLowerCase() !== String(item.original_item_name ?? '').toLowerCase(),
      price: isNumber(item.estimated_price) ? item.estimated_price : null,
      // The reference list has a product and price for it; otherwise the
      // service guessed both from the ingredient's category.
      roughEstimate: item.data_source !== 'local_inventory_reference',
    })
  })
  return [...groups].map(([name, entries]) => ({ name, items: entries }))
}

export function total(shopping) {
  return isNumber(shopping?.total_estimated_cost) ? shopping.total_estimated_cost : null
}
