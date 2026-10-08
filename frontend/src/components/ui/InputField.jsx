function InputField({ helperText, label, ...inputProps }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-gray-900">{label}</span>
      <input
        className="mt-2 w-full rounded-lg border border-gray-200 bg-white px-3.5 py-2.5 text-sm text-gray-900 shadow-sm outline-none transition-all duration-200 placeholder:text-gray-400 focus:border-transparent focus:ring-2 focus:ring-emerald-500"
        {...inputProps}
      />
      {helperText && <span className="mt-1.5 block text-xs leading-5 text-gray-500">{helperText}</span>}
    </label>
  )
}

export default InputField
