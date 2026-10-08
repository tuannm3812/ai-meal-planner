function ErrorBanner({ children }) {
  return (
    <div className="rounded-xl border border-red-100 bg-red-50 p-3 text-sm leading-6 text-red-700 shadow-sm">
      {children}
    </div>
  )
}

export default ErrorBanner
