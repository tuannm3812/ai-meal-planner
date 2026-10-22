import { formatCurrency } from '../../lib/format'
import { aisles, storeOf, total } from './shopping'

// The shopping list by aisle, with a checkbox per item (docs/8_design.md
// §3.3). The ticks belong to the flow, which keeps them while the person
// moves between steps and clears them for a new plan; they are never sent
// or stored.
// `location` is the one the plan was requested for, not the live input.
function ShoppingList({ shopping, location, ticked, onToggle }) {
  const store = storeOf(shopping)
  const groups = aisles(shopping)
  const sum = total(shopping)
  const count = groups.reduce((n, group) => n + group.items.length, 0)

  return (
    <section
      aria-labelledby="shopping-heading"
      className="rounded-[20px] border border-line bg-surface p-6"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="font-display text-xl font-bold text-ink" id="shopping-heading">
          Shopping list
        </h3>
        {count > 0 && (
          <p className="text-sm text-muted">
            {ticked.size} of {count} ticked
          </p>
        )}
      </div>

      {location && (
        <p className="mt-1 text-sm text-muted">For shopping near &ldquo;{location}&rdquo;</p>
      )}

      {store && (
        <p className="mt-1 text-sm text-muted">
          {store.name}
          {store.address && ` · ${store.address}`}
          {store.guessed && (
            <span className="block">
              A likely store for your area, not one matched to your address.
            </span>
          )}
        </p>
      )}

      {count === 0 ? (
        <p className="mt-4 rounded-[14px] bg-ground p-4 text-sm text-muted">
          No shopping list came with this plan.
        </p>
      ) : (
        <div className="mt-4 flex flex-col gap-5">
          {groups.map((group) => (
            <fieldset key={group.name}>
              <legend className="text-xs font-semibold uppercase tracking-wider text-muted">
                {group.name}
              </legend>
              <ul className="mt-2 divide-y divide-line">
                {group.items.map((item) => (
                  <li key={item.id}>
                    <label className="flex min-h-[44px] cursor-pointer items-center gap-3 py-2">
                      <input
                        checked={ticked.has(item.id)}
                        className="h-5 w-5 shrink-0 accent-ink"
                        onChange={() => onToggle(item.id)}
                        type="checkbox"
                      />
                      <span className="min-w-0 flex-1">
                        <span
                          className={`block text-ink ${ticked.has(item.id) ? 'text-muted line-through' : ''}`}
                        >
                          {item.product}
                        </span>
                        {(item.ingredient !== item.product || item.roughEstimate) && (
                          <span className="block text-xs text-muted">
                            {item.ingredient !== item.product && `For ${item.ingredient}`}
                            {item.ingredient !== item.product && item.roughEstimate && ' · '}
                            {item.roughEstimate && 'Product and price guessed from its category'}
                          </span>
                        )}
                      </span>
                      {item.price !== null && (
                        <span className="shrink-0 text-ink">{formatCurrency(item.price)}</span>
                      )}
                    </label>
                  </li>
                ))}
              </ul>
            </fieldset>
          ))}
        </div>
      )}

      {count > 0 && sum !== null && (
        <div className="mt-4 flex items-baseline justify-between border-t border-line pt-4 font-semibold text-ink">
          <span>Estimated total</span>
          <span>{formatCurrency(sum)}</span>
        </div>
      )}

      {count > 0 && (
        <p className="mt-2 text-sm text-muted">
          Prices are estimates from a local reference list, not live store prices.
        </p>
      )}
    </section>
  )
}

export default ShoppingList
