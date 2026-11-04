import { defineConfig, minimal2023Preset } from '@vite-pwa/assets-generator/config'

export default defineConfig({
  headLinkOptions: {
    preset: '2023',
  },
  preset: {
    ...minimal2023Preset,
    transparent: {
      ...minimal2023Preset.transparent,
      favicons: [],
    },
    maskable: {
      ...minimal2023Preset.maskable,
      padding: 0.3,
      resizeOptions: { background: '#ffffff' },
    },
    apple: {
      ...minimal2023Preset.apple,
      padding: 0.2,
      resizeOptions: { background: '#ffffff' },
    },
  },
  images: ['public/logo-mark.png'],
})
