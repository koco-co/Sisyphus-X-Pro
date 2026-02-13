import { forwardRef } from 'react'

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  React.ComponentProps<'textarea'>
>((props, ref) => {
  return (
    <textarea
      ref={ref}
      className="w-full px-3 py-2 bg-background border border-border rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      {...props}
    />
  )
})
