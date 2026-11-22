// The one source of every colour in the React app (DESIGN.md §3, DEC-38).
// tailwind.config.js maps these to class names, and SVG charts import them.
// No other file may hold a raw hex value; tokens.test.js enforces that.

// Neutrals: text, lines and the grounds pages sit on.
export const neutral = {
  ink: '#15291F',
  inkRaised: '#1F3D2E',
  muted: '#4B5B52',
  onInkMuted: '#C9D3CC',
  line: '#DDE3DA',
  ground: '#EEF4EF',
  tint: '#DCEEE1',
  surface: '#FFFFFF',
}

// Brand: tomato is the one call to action; leaf and lime colour icons.
export const brand = {
  tomato: '#C8431F',
  tomatoText: '#B23A17',
  leaf: '#1B5E3F',
  lime: '#7AD151',
}

// Status: each a background and the text that sits on it.
export const status = {
  successBg: '#E3EFE6',
  successFg: '#1B5E3F',
  estimateBg: '#FBEBD6',
  estimateFg: '#7A4A0C',
  dangerBg: '#FBE4DD',
  dangerFg: '#9B2C12',
  dangerOnInk: '#FFD2BC',
}

// Data: the Viridis ramp, the three macro stops, and the "recommended range"
// band. Macro colours mean only their macro, never an icon or a button.
export const VIRIDIS = ['#440154', '#414487', '#2A788E', '#22A884', '#7AD151', '#FDE725']
export const MACRO_COLORS = { protein: VIRIDIS[0], carbs: VIRIDIS[2], fat: VIRIDIS[3] }
export const data = { band: '#C6E3CF' }

// Food: used only inside the dish drawings, never in the interface.
export const food = {
  plate: '#FFFFFF',
  plateRim: '#DCEEE1',
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
