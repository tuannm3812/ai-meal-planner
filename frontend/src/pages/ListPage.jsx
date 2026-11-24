import { useState } from 'react'

import { usePlannerContext } from '../app/PlannerContext'
import Icon from '../components/icons/Icon'
import { Search } from '../components/icons/glyphs'
import PriceTag from '../components/ui/PriceTag'
import { pageShell, sectionHeading } from '../components/ui/styles'
import MealGrid from '../features/meals/MealGrid'
import { searchMeals } from '../features/meals/meals'
import { useMealLists } from '../features/meals/useMealLists'

// My meals and Past plans share one layout: a heading with its count, a search
// box once there is something to search, then cards (My meals) or dated rows
// (Past plans).
function ListPage({ title, intro, Icon: glyph, pick, empty, rows = false, noun = 'meal' }) {
  const { userId, hasProfile } = usePlannerContext()
  const lists = useMealLists(userId, { enabled: hasProfile })
  const [query, setQuery] = useState('')
  const all = pick(lists)
  const found = searchMeals(all, query)
  const searching = query.trim() !== ''
  return (
    <main className={`${pageShell} flex flex-col gap-6 py-10`}>
      <div className="flex flex-wrap items-end justify-between gap-x-8 gap-y-4">
        <div className="min-w-0">
          <h1 className={`${sectionHeading} flex-wrap text-4xl`}>
            <Icon as={glyph} size="lg" tone="light" />
            {title}
            {lists.status === 'ready' && all.length > 0 && (
              <PriceTag className="font-mono" tone="accent">
                {all.length} {all.length === 1 ? noun : `${noun}s`}
              </PriceTag>
            )}
          </h1>
          <p className="mt-2 max-w-3xl text-muted">{intro}</p>
        </div>
        {all.length > 1 && (
          <div className="flex min-h-[52px] w-full items-center gap-3 rounded-2xl border border-line bg-surface px-4 focus-within:border-ink focus-within:ring-2 focus-within:ring-cobalt sm:w-[320px]">
            <Icon as={Search} size="sm" tone="light" />
            <label className="sr-only" htmlFor="list-search">
              Search {title.toLowerCase()}
            </label>
            <input
              className="min-w-0 flex-1 border-0 bg-transparent text-[15px] text-ink outline-none placeholder:text-muted"
              id="list-search"
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search by meal or craving"
              type="search"
              value={query}
            />
          </div>
        )}
      </div>
      {searching && (
        <p className="text-sm text-muted" role="status">
          {found.length} of {all.length} match &ldquo;{query.trim()}&rdquo;.
        </p>
      )}
      <MealGrid
        empty={searching ? 'Nothing matches that search.' : empty}
        lists={lists}
        meals={found}
        rows={rows}
      />
    </main>
  )
}

export default ListPage
