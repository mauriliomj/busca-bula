const WHITE = '#ffffff'
const BLACK = '#000000'

function parseHexColor(hex) {
  const value = hex.replace('#', '')
  return [0, 2, 4].map((offset) => parseInt(value.slice(offset, offset + 2), 16))
}

function formatHexColor(channels) {
  return `#${channels.map((channel) => Math.round(channel).toString(16).padStart(2, '0')).join('')}`
}

export function mixColors(color, target, targetWeight) {
  const base = parseHexColor(color)
  const mixed = parseHexColor(target)
  return formatHexColor(base.map((channel, index) => channel * (1 - targetWeight) + mixed[index] * targetWeight))
}

export function buildBrandPalette(corPrimaria, corSecundaria) {
  const palette = {}
  if (corPrimaria) {
    palette['--brand-primary'] = corPrimaria
    palette['--brand-primary-dark'] = mixColors(corPrimaria, BLACK, 0.15)
    palette['--brand-primary-soft'] = mixColors(corPrimaria, WHITE, 0.85)
  }
  if (corSecundaria) {
    palette['--brand-secondary'] = corSecundaria
  }
  return palette
}
