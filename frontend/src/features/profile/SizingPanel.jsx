// How a meal is sized, in four steps, on the one dark panel of the page.
// `stacked` keeps the steps in one column where the panel is narrow.
function SizingPanel({ stacked = false }) {
  return (
    <aside aria-label="How your meal is sized" className="self-start rounded-3xl bg-ink p-7 text-ground">
      <p className="text-sm text-ground/75">How your meal is sized</p>
      <ol
        className={`mt-4 grid list-decimal gap-x-10 gap-y-3.5 pl-5 text-base leading-6 ${
          stacked ? '' : 'md:grid-cols-2 2xl:grid-cols-1'
        }`}
      >
        <li>
          Your body and activity level set the energy you burn in a day, and a trained model adds
          today&rsquo;s workout.
        </li>
        <li>Your goal sets the calories for this meal, with a safe floor when losing weight.</li>
        <li>Portions are resized so protein, carbs and fat sit inside recommended ranges.</li>
        <li>Nutrition is checked against food data, and anything estimated is labelled.</li>
      </ol>
      <p className="mt-6 border-t border-ground/20 pt-4 text-sm text-ground/75">
        A planning aid, not medical advice.
      </p>
    </aside>
  )
}

export default SizingPanel
