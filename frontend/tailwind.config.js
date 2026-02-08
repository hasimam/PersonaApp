module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3A506B',
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        accent: '#C5A880',
        cream: '#F6F1EA',
        sand: '#E0D6CC',
        canvas: '#F9F7F2',
        muted: '#6F7472',
        ink: '#2B2E2D',
      },
      boxShadow: {
        'soft-card': '0 8px 30px rgba(58,80,107,0.08)',
        'soft-float': '0 12px 40px rgba(58,80,107,0.12)',
      },
      borderRadius: {
        soft: '22px',
        'soft-xl': '24px',
      },
    },
  },
  plugins: [],
}
