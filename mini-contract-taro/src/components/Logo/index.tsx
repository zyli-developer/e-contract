import { Image } from '@tarojs/components'

interface Props {
  size?: number | string
  color?: string
}

export default function Logo({ size = 144, color = '#678EBA' }: Props) {
  // SVG 模板，使用用户提供的路径和参数
  const encodedColor = color.replace('#', '%23')
  const svgContent = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 144 144" width="144" height="144">
      <g stroke="${encodedColor}" fill="none" stroke-linecap="round" stroke-linejoin="round">
        <path d="M 26 78 L 72 36 L 118 78 M 40 66 V 106 Q 40 112 46 112 H 98 Q 104 112 104 106 V 66" stroke-width="8" />
        <path d="M 60 70 V 70 M 84 70 V 70" stroke-width="8" />
        <path d="M 62 82 Q 72 92 82 82" stroke-width="6" />
      </g>
      <circle cx="108" cy="32" r="8" fill="${encodedColor}" />
    </svg>
  `.trim().replace(/\n/g, '').replace(/>\s+</g, '><')

  const dataUri = `data:image/svg+xml;charset=utf-8,${svgContent}`

  return (
    <Image
      src={dataUri}
      style={{
        width: typeof size === 'number' ? `${size}rpx` : size,
        height: typeof size === 'number' ? `${size}rpx` : size,
        display: 'block'
      }}
      mode="aspectFit"
    />
  )
}
