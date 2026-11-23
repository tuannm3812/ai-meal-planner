// Every interface icon goes through here (DESIGN.md §5, DEC-38): Lucide at
// one stroke, three sizes, and a colour taken from the surface it sits on.
// Icons are decorative; the words beside them carry the meaning.
const ICON_SIZES = { sm: 20, md: 24, lg: 32, xl: 48 }
const ICON_STROKE = 1.75

const TONES = {
  light: 'text-leaf', // on ground, tint or a white card
  ink: 'text-lime', // on the ink banners and top bar
  current: '', // inside a button or notice: the text colour
}

function Icon({ as: Glyph, size = 'md', tone = 'current', filled = false, className = '' }) {
  return (
    <Glyph
      aria-hidden="true"
      className={`shrink-0 ${TONES[tone]} ${className}`.trim()}
      fill={filled ? 'currentColor' : 'none'}
      focusable="false"
      size={ICON_SIZES[size]}
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={ICON_STROKE}
    />
  )
}

export default Icon
