import type { ReactNode, CSSProperties } from 'react'
import { clsx } from 'clsx'

interface Props {
  children: ReactNode
  className?: string
  style?: CSSProperties
}

export default function FullBleedSection({ children, className, style }: Props) {
  return (
    <section className={clsx('w-full', className)} style={style}>
      <div className="max-w-[1440px] mx-auto px-8 md:px-16 xl:px-24">
        {children}
      </div>
    </section>
  )
}
