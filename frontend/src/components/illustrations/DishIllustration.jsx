import { brand, food, neutral, VIRIDIS } from '../../theme/tokens'
import { dishType } from './dishType'

// Flat food drawings (DESIGN.md §5, DEC-37): no outlines, no gradients, the
// palette plus the food colours in theme/tokens.js. Each stands for a kind of
// dish, so it is decorative and hidden from assistive technology.
const C = {
  ink: neutral.ink,
  teal: VIRIDIS[2],
  green: VIRIDIS[3],
  lime: brand.lime,
  tomato: brand.tomato,
  ...food,
}

const Leaf = ({ x, y, flip = false, color = C.green }) => (
  <path
    d={flip ? `M${x} ${y}c-8-12-24-12-30-4 10 0 20 2 30 4z` : `M${x} ${y}c8-12 24-12 30-4-10 0-20 2-30 4z`}
    fill={color}
  />
)

// A bowl seen from the side: body, a darker band and what sits on top.
const Bowl = ({ color = C.teal, band = C.tealDark, children }) => (
  <>
    <path d="M30 70h140a70 58 0 0 1-140 0z" fill={color} />
    <path d="M30 70h140a70 58 0 0 1-7 26H37a70 58 0 0 1-7-26z" fill={band} />
    {children}
  </>
)

// A plate seen from above.
const Plate = ({ children }) => (
  <>
    <ellipse cx="100" cy="76" rx="84" ry="52" fill={C.plateRim} />
    <ellipse cx="100" cy="76" rx="70" ry="42" fill={C.plate} />
    {children}
  </>
)

const DRAWINGS = {
  rice: () => (
    <Bowl>
      <path d="M40 70c6-40 114-40 120 0z" fill={C.rice} />
      <rect x="66" y="48" width="20" height="13" rx="5" fill={C.chicken} />
      <rect x="106" y="42" width="22" height="14" rx="5" fill={C.chicken} />
      <ellipse cx="96" cy="62" rx="9" ry="6" fill={C.egg} />
      <circle cx="58" cy="64" r="4.5" fill={C.green} />
      <circle cx="90" cy="46" r="4.5" fill={C.green} />
      <circle cx="140" cy="60" r="4.5" fill={C.green} />
      <rect x="120" y="60" width="7" height="7" rx="1.5" fill={C.carrot} />
    </Bowl>
  ),
  stirfry: () => (
    <>
      <rect x="150" y="62" width="44" height="8" rx="4" fill={C.ink} />
      <path d="M24 66h132a66 40 0 0 1-132 0z" fill={C.ink} />
      <path d="M34 66c8-26 104-26 112 0z" fill={C.tortilla} />
      <rect x="54" y="50" width="20" height="12" rx="5" fill={C.chicken} />
      <rect x="96" y="46" width="22" height="13" rx="5" fill={C.chicken} />
      <Leaf x={76} y={58} />
      <Leaf x={112} y={62} color={C.lime} />
      <rect x="84" y="44" width="8" height="8" rx="2" fill={C.tomato} />
    </>
  ),
  noodles: () => (
    <Bowl color={C.tomato} band={C.tomatoDark}>
      <path d="M40 70c6-34 114-34 120 0z" fill={C.noodle} />
      <path
        d="M52 62c10-8 20 8 30 0s20 8 30 0 20 8 30 0M56 52c10-8 20 8 30 0s20 8 30 0 16 6 24 0"
        fill="none"
        stroke={C.noodleLine}
        strokeWidth="3"
        strokeLinecap="round"
      />
      <rect x="60" y="14" width="6" height="60" rx="3" fill={C.ink} transform="rotate(-24 63 44)" />
      <rect x="74" y="12" width="6" height="60" rx="3" fill={C.ink} transform="rotate(-16 77 42)" />
      <Leaf x={116} y={50} />
    </Bowl>
  ),
  pasta: () => (
    <Plate>
      <path
        d="M62 76c10-14 22 10 32-4s22 12 32-2 14 10 18 4M66 88c10-12 22 8 32-4s22 10 32-2"
        fill="none"
        stroke={C.noodle}
        strokeWidth="9"
        strokeLinecap="round"
      />
      <circle cx="84" cy="72" r="9" fill={C.tomato} />
      <circle cx="112" cy="84" r="9" fill={C.tomato} />
      <Leaf x={92} y={64} />
    </Plate>
  ),
  curry: () => (
    <Bowl color={C.tomato} band={C.tomatoDark}>
      <path d="M40 70c6-30 114-30 120 0z" fill={C.curry} />
      <circle cx="72" cy="58" r="7" fill={C.bean} />
      <circle cx="94" cy="52" r="7" fill={C.bean} />
      <circle cx="116" cy="58" r="7" fill={C.bean} />
      <circle cx="136" cy="64" r="6" fill={C.bean} />
      <Leaf x={92} y={44} />
    </Bowl>
  ),
  soup: () => (
    <Bowl>
      <path d="M40 70c6-18 114-18 120 0z" fill={C.broth} />
      <circle cx="74" cy="64" r="6" fill={C.carrot} />
      <rect x="96" y="58" width="16" height="10" rx="4" fill={C.chicken} />
      <circle cx="126" cy="64" r="5" fill={C.green} />
      <path d="M86 40c-6-8 6-12 0-20M104 40c-6-8 6-12 0-20" fill="none" stroke={C.plateRim} strokeWidth="4" strokeLinecap="round" />
    </Bowl>
  ),
  salad: () => (
    <Bowl color={C.green} band={C.greenDark}>
      <path d="M40 70c4-36 116-36 120 0z" fill={C.lime} />
      <Leaf x={52} y={60} />
      <Leaf x={120} y={56} flip />
      <circle cx="84" cy="54" r="8" fill={C.tomato} />
      <circle cx="118" cy="62" r="7" fill={C.tomato} />
      <rect x="94" y="56" width="18" height="11" rx="4" fill={C.chicken} />
      <circle cx="70" cy="64" r="5" fill={C.egg} />
    </Bowl>
  ),
  taco: () => (
    <>
      <path d="M34 104a66 66 0 0 1 132 0z" fill={C.tortilla} />
      <path d="M46 98c10-34 98-34 108 0z" fill={C.lime} />
      <rect x="62" y="70" width="22" height="12" rx="5" fill={C.chicken} />
      <rect x="102" y="66" width="22" height="12" rx="5" fill={C.chicken} />
      <circle cx="90" cy="64" r="6" fill={C.tomato} />
      <circle cx="132" cy="80" r="6" fill={C.tomato} />
      <rect x="30" y="102" width="140" height="8" rx="4" fill={C.ink} opacity="0.15" />
    </>
  ),
  eggs: () => (
    <Plate>
      <rect x="44" y="52" width="62" height="50" rx="14" fill={C.bread} />
      <rect x="50" y="58" width="50" height="38" rx="10" fill={C.crumb} />
      <ellipse cx="132" cy="76" rx="30" ry="22" fill={C.plate} stroke={C.plateRim} strokeWidth="2" />
      <circle cx="132" cy="76" r="11" fill={C.egg} />
      <Leaf x={64} y={80} />
    </Plate>
  ),
  oats: () => (
    <Bowl>
      <path d="M40 70c6-28 114-28 120 0z" fill={C.oat} />
      <ellipse cx="78" cy="56" rx="12" ry="6" fill={C.banana} />
      <ellipse cx="102" cy="52" rx="12" ry="6" fill={C.banana} />
      <circle cx="124" cy="58" r="5" fill={C.berry} />
      <circle cx="134" cy="62" r="5" fill={C.berry} />
      <circle cx="64" cy="64" r="3" fill={C.bread} />
    </Bowl>
  ),
  plate: () => (
    <Plate>
      <path d="M56 70c12-18 60-18 74-4 4 12-4 20-16 20H66c-12 0-18-8-10-16z" fill={C.salmon} />
      <path d="M72 64l5 18M90 60l5 22M108 62l5 20" stroke={C.salmonLine} strokeWidth="3" strokeLinecap="round" />
      <circle cx="140" cy="86" r="4" fill={C.grain} />
      <circle cx="148" cy="94" r="4" fill={C.grain} />
      <circle cx="152" cy="82" r="4" fill={C.grain} />
      <circle cx="142" cy="100" r="4" fill={C.grain} />
      <Leaf x={110} y={102} />
      <circle cx="58" cy="94" r="7" fill={C.potato} />
    </Plate>
  ),
  bowl: () => (
    <Bowl>
      <path d="M40 70c6-36 114-36 120 0z" fill={C.rice} />
      <path d="M44 70c4-24 46-30 56-26v26z" fill={C.grain} />
      <rect x="100" y="46" width="24" height="14" rx="5" fill={C.chicken} />
      <circle cx="136" cy="60" r="7" fill={C.tomato} />
      <Leaf x={66} y={52} />
      <Leaf x={116} y={66} color={C.lime} />
    </Bowl>
  ),
}

function DishIllustration({ mealName, type, className = '' }) {
  const kind = type ?? dishType(mealName)
  const Drawing = DRAWINGS[kind] ?? DRAWINGS.bowl
  return (
    <svg aria-hidden="true" className={className} data-dish={kind} focusable="false" viewBox="0 0 200 140">
      <ellipse cx="100" cy="130" rx="74" ry="6" fill={C.ink} opacity="0.12" />
      <Drawing />
    </svg>
  )
}

export default DishIllustration
