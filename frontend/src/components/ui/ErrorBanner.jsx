function ErrorBanner({ children }) {
  return (
    <div className="rounded-xl bg-danger-bg p-3 text-sm leading-6 text-danger-fg">
      {children}
    </div>
  )
}

export default ErrorBanner
