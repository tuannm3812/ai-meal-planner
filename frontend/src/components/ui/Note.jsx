import Icon from '../icons/Icon'
import { Info } from '../icons/glyphs'

// A quiet aside under a field or a form (DESIGN.md §6): an icon, then the
// note, on a soft ground. Not for errors, which use the danger pair.
function Note({ children, className = '', onGround = false }) {
  return (
    <p className={`flex gap-2.5 rounded-xl ${onGround ? 'bg-surface' : 'bg-ground'} px-3.5 py-3 text-sm leading-6 text-muted ${className}`}>
      <Icon as={Info} className="mt-0.5" size="sm" tone="light" />
      <span className="min-w-0">{children}</span>
    </p>
  )
}

export default Note
