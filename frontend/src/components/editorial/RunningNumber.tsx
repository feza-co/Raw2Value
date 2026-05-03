import { useEffect, useRef, useState } from 'react'

interface Props {
  target: number
  duration?: number
  prefix?: string
  suffix?: string
  className?: string
}

export default function RunningNumber({ target, duration = 1800, prefix = '', suffix = '', className }: Props) {
  const [display, setDisplay] = useState(0)
  const ref = useRef<HTMLSpanElement>(null)
  const started = useRef(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started.current) {
          started.current = true
          const start = performance.now()
          const step = (now: number) => {
            const t = Math.min((now - start) / duration, 1)
            const ease = 1 - Math.pow(1 - t, 4)
            setDisplay(Math.round(ease * target))
            if (t < 1) requestAnimationFrame(step)
          }
          requestAnimationFrame(step)
        }
      },
      { threshold: 0.3 },
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [target, duration])

  return (
    <span ref={ref} className={className}>
      {prefix}{display.toLocaleString('tr-TR')}{suffix}
    </span>
  )
}
