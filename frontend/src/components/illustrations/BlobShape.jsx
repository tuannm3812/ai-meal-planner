import { brand } from '../../theme/tokens'

// The one soft shape behind a banner illustration (DESIGN.md §6).
function BlobShape({ className = '', color = brand.peach }) {
  return (
    <svg aria-hidden="true" className={className} focusable="false" viewBox="0 0 620 620">
      <path
        d="M310 40c120 0 250 70 260 200s-60 260-200 300S60 520 50 380 190 40 310 40z"
        fill={color}
      />
    </svg>
  )
}

export default BlobShape
