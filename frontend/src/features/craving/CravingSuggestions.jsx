import { CRAVING_SUGGESTIONS } from './craving'

// Suggestion chips: each fills the craving with a meal the menu really has.
function CravingSuggestions({ onPick }) {
  return (
    <div>
      <p className="text-sm text-muted" id="craving-suggestions">
        Or try one of these
      </p>
      <ul aria-labelledby="craving-suggestions" className="mt-2 flex flex-wrap gap-2">
        {CRAVING_SUGGESTIONS.map((suggestion) => (
          <li key={suggestion.meal}>
            <button
              className="min-h-[44px] rounded-full border border-line bg-surface px-3.5 text-sm text-ink hover:border-ink focus:outline-none focus-visible:ring-2 focus-visible:ring-ink"
              onClick={() => onPick(suggestion.label.toLowerCase())}
              type="button"
            >
              {suggestion.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default CravingSuggestions
