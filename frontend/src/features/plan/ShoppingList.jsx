import { useState } from 'react'

import Icon from '../../components/icons/Icon'
import { Copy, Printer, ShoppingCart } from '../../components/icons/glyphs'
import { secondaryButton } from '../../components/ui/styles'
import { formatCurrency } from '../../lib/format'
import { aisles, storeOf, total } from './shopping'
import { shoppingText } from './shoppingText'

// The receipt's torn bottom edge: a row of teeth, outlined like the card.
function TornEdge() {
  return (
    <svg aria-hidden="true" className="block h-3 w-full" focusable="false">
      <defs>
        <pattern height="12" id="receipt-teeth" patternUnits="userSpaceOnUse" width="16">
          <path className="fill-surface stroke-ink" d="M0 0 L8 10 L16 0" strokeWidth="1" />
        </pattern>
      </defs>
      <rect fill="url(#receipt-teeth)" height="12" width="100%" />
    </svg>
  )
}

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
    <section aria-labelledby="shopping-heading" data-print="shopping">
      {/* A till receipt (DESIGN.md §6): a navy outline, mono type, dashed
          rules and a torn bottom edge. */}
      <div className="rounded-t-2xl border border-b-0 border-ink bg-surface px-5 pb-5 pt-6 font-mono text-[13px] leading-relaxed text-ink sm:px-6">
        <div className="flex flex-col items-center gap-1 text-center">
          <Icon as={ShoppingCart} size="lg" tone="light" />
          <h2
            className="font-display text-[22px] font-extrabold tracking-tight text-ink"
            id="shopping-heading"
          >
            Shopping list
          </h2>
          {store && (
            <p className="font-bold uppercase tracking-wide">
              {store.name}
              {store.address && ` · ${store.address}`}
            </p>
          )}
          {store?.guessed && (
            <p className="text-xs text-muted">
              A likely store for your area, not one matched to your address.
            </p>
          )}
          {location && <p className="text-xs text-muted">For shopping near &ldquo;{location}&rdquo;</p>}
        </div>

        {count === 0 ? (
          <p className="mt-4 border-t border-dashed border-muted pt-4 text-center font-sans text-sm text-muted">
            No shopping list came with this plan.
          </p>
        ) : (
          <>
            <div className="mt-4 flex justify-between border-y border-dashed border-muted py-2 text-xs uppercase tracking-wide text-muted">
              <span>
                {count} {count === 1 ? 'item' : 'items'}
              </span>
              <span>
                {ticked.size} of {count} ticked
              </span>
            </div>
            <div className="mt-3 flex flex-col gap-3">
              {groups.map((group) => (
                <fieldset key={group.name}>
                  <legend className="text-xs font-bold uppercase tracking-widest text-cobalt">
                    {group.name}
                  </legend>
                  <ul>
                    {group.items.map((item) => (
                      <li key={item.id}>
                        <label className="flex min-h-[44px] cursor-pointer items-center gap-3 py-1.5">
                          <input
                            checked={ticked.has(item.id)}
                            className="h-5 w-5 shrink-0 accent-ink"
                            onChange={() => onToggle(item.id)}
                            type="checkbox"
                          />
                          <span className="min-w-0 flex-1">
                            <span className="flex items-baseline gap-2">
                              <span className={ticked.has(item.id) ? 'text-muted line-through' : ''}>
                                {item.product}
                              </span>
                              <span
                                aria-hidden="true"
                                className="min-w-[12px] flex-1 border-b border-dotted border-line"
                              />
                              {item.price !== null && (
                                <span className="shrink-0 font-medium tabular-nums">
                                  {formatCurrency(item.price)}
                                </span>
                              )}
                            </span>
                            {(item.named || item.roughEstimate) && (
                              <span className="block text-xs text-muted">
                                {item.named && `For ${item.ingredient}`}
                                {item.named && item.roughEstimate && ' · '}
                                {item.roughEstimate && 'Rough estimate'}
                              </span>
                            )}
                          </span>
                        </label>
                      </li>
                    ))}
                  </ul>
                </fieldset>
              ))}
            </div>

            {sum !== null && (
              <div className="mt-3 flex items-baseline justify-between gap-3 border-t-2 border-dashed border-ink pt-3 text-[20px] font-bold">
                <span className="uppercase tracking-wide">Estimated total</span>
                <span className="tabular-nums">{formatCurrency(sum)}</span>
              </div>
            )}

            <p className="mt-3 border-t border-dashed border-muted pt-3 text-xs text-muted">
              Prices are estimates from a local reference list, not live store prices.
            </p>
            {anyRough && (
              <p className="mt-1 text-xs text-muted">
                A rough estimate means the product and price were guessed from the item&rsquo;s category.
              </p>
            )}

            <div className="mt-4 flex flex-wrap gap-3 font-sans print:hidden">
              <button className={`${secondaryButton} flex-1`} onClick={copy} type="button">
                <Icon as={Copy} size="sm" />
                Copy list
              </button>
              <button className={`${secondaryButton} flex-1`} onClick={() => window.print()} type="button">
                <Icon as={Printer} size="sm" />
                Print
              </button>
            </div>
          </>
        )}
        {copied && (
          <p className="mt-2 font-sans text-sm text-muted" role="status">
            {copied}
          </p>
        )}
      </div>
      <TornEdge />
    </section>
  )
}

export default ShoppingList
