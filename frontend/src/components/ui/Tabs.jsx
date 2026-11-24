import { useRef } from 'react'

// A row of tabs (DESIGN.md §6): the active one is an ink pill, as in the rail.
// The tabs stay on one row; on a phone a long label wraps inside its tab.
// Arrow keys, Home and End move between tabs; the panel is the caller's, with
// id `${idPrefix}-panel` and aria-labelledby `${idPrefix}-tab-${active}`.
function Tabs({ tabs, active, onChange, label, idPrefix }) {
  const refs = useRef({})
  const move = (event) => {
    const index = tabs.findIndex((tab) => tab.id === active)
    const last = tabs.length - 1
    const next = {
      ArrowRight: index === last ? 0 : index + 1,
      ArrowLeft: index === 0 ? last : index - 1,
      Home: 0,
      End: last,
    }[event.key]
    if (next === undefined) return
    event.preventDefault()
    onChange(tabs[next].id)
    refs.current[tabs[next].id]?.focus()
  }
  return (
    <div
      aria-label={label}
      className="flex gap-1.5 rounded-2xl bg-surface p-1.5 print:hidden"
      role="tablist"
    >
      {tabs.map((tab) => {
        const selected = tab.id === active
        return (
          <button
            aria-controls={`${idPrefix}-panel`}
            aria-selected={selected}
            className={`flex min-h-[44px] min-w-0 flex-1 items-center justify-center gap-2 rounded-xl px-2 text-center text-sm leading-tight font-semibold sm:px-4 sm:text-[15px] focus:outline-none focus-visible:ring-2 focus-visible:ring-cobalt focus-visible:ring-offset-2 ${
              selected ? 'bg-ink text-white' : 'text-ink hover:bg-tint'
            }`}
            id={`${idPrefix}-tab-${tab.id}`}
            key={tab.id}
            onClick={() => onChange(tab.id)}
            onKeyDown={move}
            ref={(node) => {
              refs.current[tab.id] = node
            }}
            role="tab"
            tabIndex={selected ? 0 : -1}
            type="button"
          >
            {tab.label}
            {tab.count !== undefined && (
              <span
                className={`rounded-full px-2 py-0.5 font-mono text-xs ${selected ? 'bg-white/15' : 'bg-tint'}`}
              >
                {tab.count}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}

export default Tabs
