module.exports = {
  content: ["./src/**/*.svelte"],
  media: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [],
  safelist: process.env.NODE_ENV === "development" ? [{ pattern: /.*/ }] : [],
};
