/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    screens: {//setting breakpoints, what's small, medium, large, xl
      sm: '480px',
      md: '768px',
      lg: '976px',
      xl: '1440px'
    },
    extend: {
      //define classes to use later
      colors: {
        'gray1': '#F1F1F1',
        'gray2': '#E3E3E3',
        'gray3': '#D5D5D5',
        'gray4': '#C8C8C8',
        'gray5': '#646464',
        'blue1': '#CCCCFF',
        'blue2': '#4757E7',
        'blue3': '#4050DE',
        'blue4': '#3C4BD1',
        'skyblue': '#1487D8',
        'darkblue': '#7D4DD0',
        'lime': '#14A202',
        'active-green': '#5ec702',
        'waiting-yellow': '#edba02',
        'unavailable-red': '#fc630a'
      }
    },
  },
  plugins: []
}