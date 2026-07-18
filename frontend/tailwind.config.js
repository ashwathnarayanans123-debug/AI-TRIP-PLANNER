/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        display: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#0b6e4f',
          700: '#065f46',
          800: '#064e3b',
          900: '#022c22',
          950: '#011c16',
        },
        saffron: {
          300: '#fbbf77',
          400: '#f59e0b',
          500: '#e87722',
          600: '#c2410c',
        },
        ink: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
      },
      backgroundImage: {
        'hero-india':
          "linear-gradient(120deg, rgba(2,6,23,0.75), rgba(11,110,79,0.45)), url('https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1920&q=80')",
        'hero-travel':
          "linear-gradient(120deg, rgba(2,6,23,0.72), rgba(11,110,79,0.45)), url('https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1920&q=80')",
        'mesh-light':
          'radial-gradient(at 20% 20%, rgba(232,119,34,0.14), transparent 45%), radial-gradient(at 80% 0%, rgba(11,110,79,0.12), transparent 40%), radial-gradient(at 50% 80%, rgba(16,185,129,0.08), transparent 45%)',
        'mesh-dark':
          'radial-gradient(at 15% 10%, rgba(232,119,34,0.12), transparent 40%), radial-gradient(at 85% 20%, rgba(11,110,79,0.18), transparent 40%), radial-gradient(at 40% 90%, rgba(2,44,34,0.35), transparent 45%)',
      },
      boxShadow: {
        glass: '0 8px 32px rgba(15, 23, 42, 0.12)',
        'glass-lg': '0 20px 50px rgba(15, 23, 42, 0.18)',
      },
      animation: {
        'fade-up': 'fadeUp 0.7s ease-out both',
        shimmer: 'shimmer 1.6s linear infinite',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(18px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
}
