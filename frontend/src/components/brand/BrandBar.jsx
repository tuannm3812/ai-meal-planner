import logoMark from '../../assets/brand/logo-mark.svg'

function BrandBar() {
  return (
    <div className="border-b border-line bg-surface">
      <div className="mx-auto flex max-w-7xl items-center gap-2.5 px-4 py-4 sm:px-6 lg:px-8">
        <img src={logoMark} alt="" width="28" height="28" />
        <span className="font-display text-xl font-bold text-ink">AI Meal Planner</span>
      </div>
    </div>
  )
}

export default BrandBar
