function SuccessBanner({ children }) {
  return (
    <div className="rounded-xl bg-success-bg p-3 text-sm leading-6 text-success-fg">
      {children}
    </div>
  )
}

export default SuccessBanner
