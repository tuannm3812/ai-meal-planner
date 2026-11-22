import { useId } from 'react'

function InputField({ error, helperText, label, ...inputProps }) {
  const id = useId()
  const errorId = `${id}-error`
  const helperId = `${id}-helper`
  const describedBy = [error && errorId, helperText && helperId].filter(Boolean).join(' ')
  return (
    <label className="block">
      <span className="text-sm font-medium text-ink">{label}</span>
      <input
        aria-describedby={describedBy || undefined}
        aria-invalid={error ? 'true' : undefined}
        className={`mt-2 w-full rounded-lg border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition-all duration-200 placeholder:text-muted focus:border-transparent focus:ring-2 focus:ring-ink ${
          error ? 'border-accent-text' : 'border-line'
        }`}
        {...inputProps}
      />
      {error && (
        <span className="mt-1.5 block text-sm text-accent-text" id={errorId}>
          {error}
        </span>
      )}
      {helperText && (
        <span className="mt-1.5 block text-xs leading-5 text-muted" id={helperId}>
          {helperText}
        </span>
      )}
    </label>
  )
}

export default InputField
