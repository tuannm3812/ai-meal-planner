export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Deliberately not exporting an axios.create() instance here. App.test.jsx mocks the
// axios module at the top level with only `default.get` and `default.post` (no
// `create`), so a configured instance would bypass that mock and break the eight-test
// regression harness. mealPlanner.js calls the default axios export directly instead.
