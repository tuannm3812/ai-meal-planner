import { useId } from 'react'

import Icon from '../../components/icons/Icon'
import { MapPin } from '../../components/icons/glyphs'

// Where the person shops, kept with their details (spec §4.2).
function LocationField({ value, error, onChange }) {
  const id = useId()
  const errorId = `${id}-error`
  return (
    <div className="max-w-md">
      <label className="flex items-center gap-2 text-sm font-medium text-ink" htmlFor={id}>
        <Icon as={MapPin} tone="light" />
        Where you shop
      </label>
      <input
        aria-describedby={error ? errorId : `${id}-help`}
        aria-invalid={error ? 'true' : undefined}
        className={`mt-1.5 h-12 w-full rounded-[10px] border bg-surface px-3.5 text-base text-ink outline-none focus:ring-2 focus:ring-ink ${
          error ? 'border-danger-fg' : 'border-line'
        }`}
        id={id}
        onChange={(event) => onChange(event.target.value)}
        value={value}
      />
      {error ? (
        <p className="mt-1.5 text-sm font-medium text-danger-fg" id={errorId}>
          {error}
        </p>
      ) : (
        <p className="mt-1.5 text-sm text-muted" id={`${id}-help`}>
          Used to pick a store for the shopping list.
        </p>
      )}
    </div>
  )
}

export default LocationField
