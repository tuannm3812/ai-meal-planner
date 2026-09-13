function SubmitButton({ isLoading, idleLabel, loadingLabel, disabled }) {
  return (
    <button
      className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition-colors duration-200 hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-gray-300"
      disabled={disabled}
      type="submit"
    >
      {isLoading && (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
      )}
      {isLoading ? loadingLabel : idleLabel}
    </button>
  )
}

export default SubmitButton
