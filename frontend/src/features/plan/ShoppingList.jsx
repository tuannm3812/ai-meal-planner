import { useState } from 'react'

import Icon from '../../components/icons/Icon'
import { Copy, Printer, ShoppingCart } from '../../components/icons/glyphs'
import { secondaryButton } from '../../components/ui/styles'
import { formatCurrency } from '../../lib/format'
import { aisles, storeOf, total } from './shopping'
import { shoppingText } from './shoppingText'

// The shopping list by aisle, with a checkbox per item (docs/8_design.md
// §3.3). The ticks belong to the flow, which keeps them while the person
// moves between steps and clears them for a new plan; they are never sent
// or stored.
// `location` is the one the plan was requested for, not the live input.
function ShoppingList({ shopping, location, ticked, onToggle, mealName }) {
  const [copied, setCopied] = useState(null)
  const store = storeOf(shopping)
  const groups = aisles(shopping)
  const sum = total(shopping)
  const count = groups.reduce((n, group) => n + group.items.length, 0)
  const anyRough = groups.some((group) => group.items.some((item) => item.roughEstimate))

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(shoppingText(shopping, mealName))
      setCopied('Copied to your clipboard.')
    } catch {
      setCopied('Could not copy. Select the list and copy it instead.')
    }
  }

  return (
    <section
      aria-labelledby="shopping-heading"
      className="rounded-3xl bg-surface p-6"
      data-print="shopping"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2
          className="flex items-center gap-3 font-display text-[26px] font-extrabold tracking-tight text-ink"
          id="shopping-heading"
        >
          <Icon as={ShoppingCart} size="lg" tone="light" />
          Shopping list
        </h2>
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
        <p className="mt-4 rounded-2xl bg-ground p-4 text-sm text-muted">
          No shopping list came with this plan.
        </p>
      ) : (
        <div className="mt-4 flex flex-col gap-5">
          {groups.map((group) => (
            <fieldset key={group.name}>
              <legend className="text-xs font-semibold uppercase tracking-wider text-cobalt">
                {group.name}
              </legend>
              <ul className="mt-1 divide-y divide-tint">
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
                        {(item.named || item.roughEstimate) && (
                          <span className="block text-xs text-muted">
                            {item.named && `For ${item.ingredient}`}
                            {item.named && item.roughEstimate && ' · '}
                            {item.roughEstimate && 'Rough estimate'}
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
        <div className="mt-4 flex items-baseline justify-between border-t border-tint pt-4 font-display text-[22px] font-extrabold text-ink">
          <span>Estimated total</span>
          <span>{formatCurrency(sum)}</span>
        </div>
      )}

      {count > 0 && (
        <p className="mt-2 text-sm text-muted">
          Prices are estimates from a local reference list, not live store prices.
        </p>
      )}
      {anyRough && (
        <p className="mt-1 text-sm text-muted">
          A rough estimate means the product and price were guessed from the item&rsquo;s category.
        </p>
      )}

      {count > 0 && (
        <div className="mt-4 flex flex-wrap gap-3 print:hidden">
          <button className={`${secondaryButton} flex-1`} onClick={copy} type="button">
            <Icon as={Copy} size="sm" />
            Copy list
          </button>
          <button className={`${secondaryButton} flex-1`} onClick={() => window.print()} type="button">
            <Icon as={Printer} size="sm" />
            Print
          </button>
        </div>
      )}
      {copied && (
        <p className="mt-2 text-sm text-muted" role="status">
          {copied}
        </p>
      )}
    </section>
  )
}

export default ShoppingList
