import Icon from '../../components/icons/Icon'
import { CircleCheck, Flame, PieChart, Scale } from '../../components/icons/glyphs'

// How a meal is sized, as four short steps on the page's one dark panel:
// an icon, a name, one line each. `stacked` keeps them in one column where
// the panel is narrow.
const STEPS = [
  { glyph: Flame, title: 'Your day', text: 'Body, activity and today’s workout set the energy you burn.' },
  { glyph: Scale, title: 'Your goal', text: 'It sets this meal’s calories, with a safe floor for weight loss.' },
  { glyph: PieChart, title: 'The balance', text: 'Portions are resized so protein, carbs and fat sit in range.' },
  { glyph: CircleCheck, title: 'The check', text: 'Nutrition is checked against food data. Estimates are labelled.' },
]

function SizingPanel({ stacked = false }) {
  return (
    <aside aria-label="How your meal is sized" className="self-start rounded-3xl bg-ink p-6 text-ground sm:p-7">
      <p className="font-display text-[20px] font-extrabold tracking-tight text-white">How your meal is sized</p>
      <ol className={`mt-5 grid gap-x-8 gap-y-5 ${stacked ? '' : 'md:grid-cols-2 2xl:grid-cols-1'}`}>
        {STEPS.map((step, index) => (
          <li className="flex items-start gap-3.5" key={step.title}>
            <span className="relative flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-ink-raised">
              <Icon as={step.glyph} tone="ink" />
              <span
                aria-hidden="true"
                className="absolute -left-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-peach font-mono text-[11px] font-bold text-ink"
              >
                {index + 1}
              </span>
            </span>
            <span className="min-w-0">
              <span className="block font-semibold text-white">{step.title}</span>
              <span className="block text-sm leading-5 text-on-ink-muted">{step.text}</span>
            </span>
          </li>
        ))}
      </ol>
      <p className="mt-6 border-t border-dashed border-ground/25 pt-4 text-sm text-on-ink-muted">
        A planning aid, not medical advice.
      </p>
    </aside>
  )
}

export default SizingPanel
