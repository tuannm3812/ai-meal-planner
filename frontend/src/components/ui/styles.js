// Shared class lists for the Market Receipt look (DESIGN.md §6), so pages stay
// consistent without a component per button.
export const focusRing =
  'focus:outline-none focus-visible:ring-2 focus-visible:ring-ink focus-visible:ring-offset-2'

export const primaryButton = `inline-flex min-h-[52px] items-center justify-center gap-2 rounded-2xl bg-accent px-7 shadow-sticker text-[17px] font-semibold text-white ${focusRing} disabled:cursor-not-allowed disabled:bg-line disabled:text-muted disabled:shadow-none`

export const secondaryButton = `inline-flex min-h-[48px] items-center justify-center gap-2 rounded-2xl border border-ink bg-surface px-5 font-semibold text-ink hover:bg-tint ${focusRing} disabled:cursor-not-allowed disabled:opacity-60`

// On an ink or cobalt banner.
export const ghostButton =
  'inline-flex min-h-[52px] items-center justify-center gap-2 rounded-2xl border border-white/40 px-5 font-semibold text-white hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-peach'

export const card = 'rounded-3xl bg-surface p-6 sm:p-7'

export const sectionHeading =
  'flex items-center gap-3 font-display text-[26px] font-extrabold tracking-tight text-ink'

// A card's heading in a narrow side column.
export const sideHeading = 'font-display text-[20px] font-extrabold tracking-tight text-ink'

// Wide screens use their width (DEC-44): up to 1,440 px beside the rail.
export const pageShell = 'mx-auto w-full max-w-6xl px-4 sm:px-6 xl:max-w-[1440px] xl:px-10'
