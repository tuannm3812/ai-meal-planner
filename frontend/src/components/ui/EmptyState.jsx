import SparkleIcon from './SparkleIcon'

function EmptyState({ isLoading, loadingTitle, loadingBody, idleTitle, idleBody }) {
  return (
    <section className="flex min-h-[420px] items-center justify-center rounded-3xl border border-transparent bg-white p-8">
      <div className="mx-auto max-w-md text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-tint text-carbs">
          {isLoading ? (
            <span className="h-6 w-6 animate-spin rounded-full border-2 border-carbs border-t-transparent" />
          ) : (
            <SparkleIcon />
          )}
        </div>
        <h2 className="mt-5 text-xl font-semibold text-ink">
          {isLoading ? loadingTitle : idleTitle}
        </h2>
        <p className="mt-3 text-sm leading-6 text-muted">{isLoading ? loadingBody : idleBody}</p>
      </div>
    </section>
  )
}

export default EmptyState
