import SectionCard from '../../components/ui/SectionCard'
import { formatCurrency } from '../../lib/format'

// The shopping list as the dashboard had it. Slice 5 of docs/8_design.md §5
// replaces it with the list by aisle.
function ShoppingSection({ shopping, location }) {
  const shoppingItems = shopping?.shopping_list || []
  return (
    <SectionCard eyebrow="Grocery" title="Supermarket">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">Nearest store</p>
          <p className="mt-1 text-xl font-semibold text-gray-900">
            {shopping?.store_details?.store_name || 'Store unavailable'}
          </p>
          <p className="mt-1 text-sm text-gray-500">
            {shopping?.store_details?.address || location}
          </p>
        </div>
        <div className="rounded-xl border border-gray-100 bg-gray-50 px-4 py-3 text-right">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            Estimated total
          </p>
          <p className="mt-1 text-2xl font-bold tracking-tight text-gray-900">
            {formatCurrency(shopping?.total_estimated_cost)}
          </p>
        </div>
      </div>

      <div className="mt-6 overflow-hidden rounded-xl bg-gray-50 shadow-sm">
        <div className="divide-y divide-gray-100 bg-white">
          {shoppingItems.map((item) => (
            <div
              className="flex items-center justify-between gap-4 px-4 py-4 transition-colors duration-150 hover:bg-gray-50"
              key={item.store_product_name}
            >
              <div className="min-w-0">
                <p className="truncate font-medium text-gray-900">
                  {item.store_product_name}
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  {item.original_item_name} - {item.category_or_aisle}
                </p>
              </div>
              <p className="shrink-0 font-semibold text-gray-900">
                {formatCurrency(item.estimated_price)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </SectionCard>
  )
}

export default ShoppingSection
