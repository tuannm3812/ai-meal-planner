import { useState } from 'react'

import { sendFeedback } from '../../api/mealPlanner'
import Icon from '../../components/icons/Icon'
import { Bookmark } from '../../components/icons/glyphs'
import { feedbackErrorMessage, feedbackPayload, isNotImplemented } from './feedback'

// "Save meal" on the plan banner. Saving is one-way: the server's feedback is
// append-only, so there is no unsave (spec §4.4).
function SaveButton({ plan, userId, saved, onSaved, onHosted }) {
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')

  const save = async () => {
    setSending(true)
    setError('')
    try {
      await sendFeedback(feedbackPayload(plan, userId, { saved: true }))
      onSaved()
    } catch (requestError) {
      if (isNotImplemented(requestError)) onHosted()
      else setError(feedbackErrorMessage(requestError))
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex flex-col gap-1">
      <button
        className={`inline-flex min-h-[52px] items-center gap-2.5 rounded-2xl px-6 text-base font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-lime disabled:cursor-default ${
          saved ? 'bg-lime text-ink' : 'bg-accent text-white'
        }`}
        disabled={saved || sending}
        onClick={save}
        type="button"
      >
        <Icon as={Bookmark} filled={saved} />
        {saved ? 'Saved to My meals' : sending ? 'Saving…' : 'Save meal'}
      </button>
      {error && (
        <p className="text-sm text-danger-on-ink" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

export default SaveButton
