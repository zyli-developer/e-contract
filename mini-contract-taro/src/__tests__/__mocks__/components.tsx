import React from 'react'

export const View = (props: any) => <div {...props} />
export const Text = (props: any) => <span {...props} />
export const Input = (props: any) => {
  const { onInput, ...rest } = props
  return (
    <input
      {...rest}
      onChange={(e) => onInput?.({ detail: { value: e.target.value } })}
    />
  )
}
export const WebView = (props: any) => <iframe {...props} />
export const Image = (props: any) => <img {...props} />
