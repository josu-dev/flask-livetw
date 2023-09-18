// Docs: https://tailwindcss.com/docs/configuration

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '{content_glob_placeholder}',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/container-queries'),
  ],
}
