import logoMark from '../../assets/brand/logo-mark.svg'

// The brand, with room on the right for the app's few secondary links.
function BrandBar({ children }) {
  return (
    <header className="border-b border-line bg-surface">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-4 sm:px-6">
        <div className="flex items-center gap-2.5">
          <img src={logoMark} alt="" width="28" height="28" />
          <span className="font-display text-xl font-bold text-ink">AI Meal Planner</span>
        </div>
        {children}
      </div>
    </header>
  )
}

export default BrandBar
