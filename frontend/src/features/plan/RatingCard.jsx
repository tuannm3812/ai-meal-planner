import { Star } from 'lucide-react'
import { useId, useState } from 'react'

import { sendFeedback } from '../../api/mealPlanner'
import { feedbackErrorMessage, feedbackPayload, isNotImplemented } from './feedback'

const STARS = [1, 2, 3, 4, 5]

// "How was it?": five stars as a radio group and an optional note, sent once
// per plan with POST /meal-feedback.
function RatingCard({ plan, userId, sentRating, onRated, onHosted }) {
  const noteId = useId()
  const [rating, setRating] = useState(0)
  const [notes, setNotes] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const shown = sentRating ?? rating

  const send = async (event) => {
    event.preventDefault()
    if (!rating) return
    setSending(true)
    setError('')
    try {
      const trimmed = notes.trim()
      await sendFeedback(feedbackPayload(plan, userId, { rating, notes: trimmed || null }))
      onRated(rating)
    } catch (requestError) {
      if (isNotImplemented(requestError)) onHosted()
      else setError(feedbackErrorMessage(requestError))
    } finally {
      setSending(false)
    }
  }

  return (
    <section aria-labelledby="rating-heading" className="rounded-3xl bg-ink p-6 text-white print:hidden">
      <h2 className="font-display text-[22px] font-extrabold" id="rating-heading">
        How was it?
      </h2>
      {sentRating ? (
        <p className="mt-1 text-sm text-[#C9D3CC]" role="status">
          Thanks. You rated it {sentRating} out of 5.
        </p>
      ) : (
        <p className="mt-1 text-sm text-[#C9D3CC]">Your rating is saved with this plan.</p>
      )}
      <form className="mt-3" onSubmit={send}>
        <fieldset disabled={Boolean(sentRating) || sending}>
          <legend className="sr-only">Rating</legend>
          <div className="flex gap-1">
            {STARS.map((n) => (
              <label className="flex h-12 w-12 cursor-pointer items-center justify-center rounded-xl focus-within:ring-2 focus-within:ring-viridis-6" key={n}>
                <input
                  checked={shown === n}
                  className="sr-only"
                  name="rating"
                  onChange={() => setRating(n)}
                  type="radio"
                  value={n}
                />
                <span className="sr-only">{n === 1 ? '1 star' : `${n} stars`}</span>
                <Star
                  aria-hidden="true"
                  className="text-viridis-6"
                  fill={n <= shown ? 'currentColor' : 'none'}
                  size={34}
                  strokeWidth={1.6}
                />
              </label>
            ))}
          </div>
          {!sentRating && (
            <>
              <label className="mt-3 block text-sm" htmlFor={noteId}>
                A note (optional)
              </label>
              <textarea
                className="mt-1.5 w-full rounded-xl border-0 px-3 py-2.5 text-base text-ink focus:outline-none focus:ring-2 focus:ring-viridis-5"
                id={noteId}
                maxLength={500}
                onChange={(event) => setNotes(event.target.value)}
                placeholder="Too salty, would make again…"
                rows={2}
                value={notes}
              />
              <button
                className="mt-3 min-h-[48px] rounded-2xl bg-white px-5 font-semibold text-ink focus:outline-none focus-visible:ring-2 focus-visible:ring-viridis-5 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={!rating || sending}
                type="submit"
              >
                {sending ? 'Sending…' : 'Save rating'}
              </button>
            </>
          )}
        </fieldset>
      </form>
      {error && (
        <p className="mt-2 text-sm text-[#FFD2BC]" role="alert">
          {error}
        </p>
      )}
    </section>
  )
}

export default RatingCard
