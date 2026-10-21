import { useId } from 'react'

function InputField({ error, helperText, label, ...inputProps }) {
  const id = useId()
  const errorId = `${id}-error`
  const helperId = `${id}-helper`
  const describedBy = [error && errorId, helperText && helperId].filter(Boolean).join(' ')
  return (
    <label className="block">
      <span className="text-sm font-medium text-gray-900">{label}</span>
      <input
        aria-describedby={describedBy || undefined}
        aria-invalid={error ? 'true' : undefined}
        className={`mt-2 w-full rounded-lg border bg-white px-3.5 py-2.5 text-sm text-gray-900 shadow-sm outline-none transition-all duration-200 placeholder:text-gray-400 focus:border-transparent focus:ring-2 focus:ring-emerald-500 ${
          error ? 'border-accent-text' : 'border-gray-200'
        }`}
        {...inputProps}
      />
      {error && (
        <span className="mt-1.5 block text-sm text-accent-text" id={errorId}>
          {error}
        </span>
      )}
      {helperText && (
        <span className="mt-1.5 block text-xs leading-5 text-gray-500" id={helperId}>
          {helperText}
        </span>
      )}
    </label>
  )
}

export default InputField
