// Every interface icon goes through here (DESIGN.md §5, DEC-38, DEC-45):
// Phosphor in its two-tone weight, four sizes, and a colour taken from the
// surface it sits on. `filled` is the solid weight, for a state that is on
// (a saved meal, a chosen star). Icons are decorative; the words beside them
// carry the meaning.
const ICON_SIZES = { sm: 20, md: 24, lg: 32, xl: 48 }

const TONES = {
  light: 'text-cobalt', // on ground, tint or a white card
  ink: 'text-peach', // on the ink or cobalt banners and the top bar
  current: '', // inside a button or notice: the text colour
}

function Icon({ as: Glyph, size = 'md', tone = 'current', filled = false, className = '' }) {
  return (
    <Glyph
      aria-hidden="true"
      className={`shrink-0 ${TONES[tone]} ${className}`.trim()}
      focusable="false"
      size={ICON_SIZES[size]}
      weight={filled ? 'fill' : 'duotone'}
    />
  )
}

export default Icon
