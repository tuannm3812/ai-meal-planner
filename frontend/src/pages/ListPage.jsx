import { usePlannerContext } from '../app/PlannerContext'
import Icon from '../components/icons/Icon'
import { pageShell, sectionHeading } from '../components/ui/styles'
import MealGrid from '../features/meals/MealGrid'
import { useMealLists } from '../features/meals/useMealLists'

// My meals and Past plans share one layout: a heading, a line, the cards.
function ListPage({ title, intro, Icon: glyph, pick, empty }) {
  const { userId, hasProfile } = usePlannerContext()
  const lists = useMealLists(userId, { enabled: hasProfile })
  return (
    <main className={`${pageShell} flex flex-col gap-5 py-10`}>
      <div>
        <h1 className={`${sectionHeading} text-4xl`}>
          <Icon as={glyph} size="lg" tone="light" />
          {title}
        </h1>
        <p className="mt-2 text-muted">{intro}</p>
      </div>
      <MealGrid empty={empty} lists={lists} meals={pick(lists)} />
    </main>
  )
}

export default ListPage
