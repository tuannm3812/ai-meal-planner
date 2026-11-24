// The one source of every colour in the React app (DESIGN.md §3, DEC-38),
// in the Market Receipt look (DEC-44).
// tailwind.config.js maps these to class names, and SVG charts import them.
// No other file may hold a raw hex value; tokens.test.js enforces that.

// Neutrals: text, lines and the grounds pages sit on.
export const neutral = {
  ink: '#14213D',
  inkRaised: '#22325A',
  muted: '#55607A',
  onInkMuted: '#DCE4FF',
  line: '#D5DBE8',
  ground: '#F4F6FB',
  tint: '#E7EDFB',
  surface: '#FFFFFF',
}

// Brand: coral is the logo's colour, and coralFill, a deeper coral that white
// text passes 4.5:1 on, fills the one call to action and price tags; cobalt is the
// brand ground for banners and colours icons on light grounds; peach colours
// icons, focus rings and highlights on ink or cobalt.
export const brand = {
  coral: '#FF5A36',
  coralFill: '#D63C1A',
  coralText: '#C2361A',
  cobalt: '#2448C9',
  cobaltRaised: '#3557D6',
  peach: '#FFD3C7',
}

// Status: each a background and the text that sits on it.
export const status = {
  successBg: '#E3F4E8',
  successFg: '#17663A',
  estimateBg: '#FFF1C2',
  estimateFg: '#6B4A00',
  dangerBg: '#FDE3DC',
  dangerFg: '#A1260E',
  dangerOnInk: '#FFC7B8',
}

// Data: the Viridis ramp, the three macro stops, and the "recommended range"
// band. Macro colours mean only their macro, never an icon or a button.
export const VIRIDIS = ['#440154', '#414487', '#2A788E', '#22A884', '#7AD151', '#FDE725']
export const MACRO_COLORS = { protein: VIRIDIS[0], carbs: VIRIDIS[2], fat: VIRIDIS[3] }
export const data = { band: '#C9D6F5' }

// Food: used only inside the dish drawings, never in the interface.
export const food = {
  plate: '#FFFFFF',
  plateRim: '#E7EDFB',
  lettuce: '#7AD151',
  tealDark: '#21677A',
  tomatoDark: '#A8361A',
  greenDark: '#1C8E70',
  rice: '#FFF6E0',
  chicken: '#D9A066',
  egg: '#F2C14E',
  carrot: '#E8833A',
  salmon: '#F08A5D',
  salmonLine: '#FFD2BC',
  curry: '#D98E2B',
  bean: '#F2D59B',
  grain: '#E3CF95',
  noodle: '#F3D27A',
  noodleLine: '#D9AE45',
  broth: '#F2B66D',
  tortilla: '#EBC57E',
  oat: '#E9D8A6',
  banana: '#F7E7A1',
  berry: '#5B3A8C',
  bread: '#D9A35F',
  crumb: '#F6DFAE',
  potato: '#E9C46A',
}
