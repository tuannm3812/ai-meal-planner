import Icon from '../icons/Icon'
import { Sparkles } from '../icons/glyphs'

function EmptyState({ isLoading, loadingTitle, loadingBody, idleTitle, idleBody }) {
  return (
    <section className="flex min-h-[420px] items-center justify-center rounded-3xl border border-transparent bg-surface p-8">
      <div className="mx-auto max-w-md text-center">
        <div className="flex justify-center">
          {isLoading ? (
            <span className="h-8 w-8 animate-spin rounded-full border-2 border-cobalt border-t-transparent" />
          ) : (
            <Icon as={Sparkles} size="lg" tone="light" />
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
