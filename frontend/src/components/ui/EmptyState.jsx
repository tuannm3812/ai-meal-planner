import SparkleIcon from './SparkleIcon'

function EmptyState({ isLoading, loadingTitle, loadingBody, idleTitle, idleBody }) {
  return (
    <section className="flex min-h-[420px] items-center justify-center rounded-2xl border border-gray-100 bg-white p-8 shadow-sm">
      <div className="mx-auto max-w-md text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 shadow-sm">
          {isLoading ? (
            <span className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
          ) : (
            <SparkleIcon />
          )}
        </div>
        <h2 className="mt-5 text-xl font-semibold text-gray-900">
          {isLoading ? loadingTitle : idleTitle}
        </h2>
        <p className="mt-3 text-sm leading-6 text-gray-500">{isLoading ? loadingBody : idleBody}</p>
      </div>
    </section>
  )
}

export default EmptyState
