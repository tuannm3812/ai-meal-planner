function SubmitButton({ isLoading, idleLabel, loadingLabel, disabled }) {
  return (
    <button
      className="flex w-full items-center justify-center gap-2 rounded-lg bg-ink px-4 py-3 text-sm font-semibold text-white transition-colors duration-200 hover:bg-ink/90 disabled:cursor-not-allowed disabled:bg-line disabled:text-muted"
      disabled={disabled}
      type="submit"
    >
      {isLoading && (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-surface border-t-transparent" />
      )}
      {isLoading ? loadingLabel : idleLabel}
    </button>
  )
}

export default SubmitButton
