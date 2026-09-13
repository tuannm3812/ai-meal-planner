// eslint-disable-next-line react-refresh/only-export-components -- TABS must live here to avoid a circular import with App.jsx
export const TABS = [
  { id: 'meal', label: 'Meal Plan' },
  { id: 'calories', label: 'Calories' },
  { id: 'history', label: 'History' },
]

function TabBar({ activeTab, onChange }) {
  return (
    <div className="inline-flex items-center gap-1 rounded-full border border-gray-100 bg-white p-1 shadow-sm">
      {TABS.map((tab) => (
        <button
          className={`rounded-full px-4 py-2 text-sm font-medium transition-colors duration-150 ${
            activeTab === tab.id
              ? 'bg-emerald-600 text-white shadow-sm'
              : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
          }`}
          key={tab.id}
          onClick={() => onChange(tab.id)}
          type="button"
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}

export default TabBar
