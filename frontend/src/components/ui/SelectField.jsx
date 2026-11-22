function SelectField({ helperText, label, options, ...selectProps }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-ink">{label}</span>
      <select
        className="mt-2 w-full rounded-lg border border-line bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-ink"
        {...selectProps}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {helperText && <span className="mt-1.5 block text-xs leading-5 text-muted">{helperText}</span>}
    </label>
  )
}

export default SelectField
