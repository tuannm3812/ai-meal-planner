function SuccessBanner({ children }) {
  return (
    <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-3 text-sm leading-6 text-emerald-700 shadow-sm">
      {children}
    </div>
  )
}

export default SuccessBanner
