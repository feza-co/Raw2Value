import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect, useRef } from 'react';

interface Props {
  label: string;
  value: number | string;
  /** count-up için sayısal hedef */
  numericTo?: number;
  /** prefix/suffix (örn. "%", " ₺") */
  prefix?: string;
  suffix?: string;
  /** ondalık */
  decimals?: number;
  /** vurgu rengi italik (em) */
  highlight?: boolean;
  /** alt yazı */
  foot?: string;
  /** yan ölçek */
  size?: 'm' | 'l' | 'xl';
  delay?: number;
  formatTr?: boolean;
}

export function NumberCallout({
  label, value, numericTo, prefix = '', suffix = '',
  decimals = 0, highlight = false, foot, size = 'l', delay = 0, formatTr = true,
}: Props) {
  const ref = useRef<HTMLSpanElement>(null);
  const mv = useMotionValue(0);
  const display = useTransform(mv, (v) => {
    const fmt = formatTr
      ? new Intl.NumberFormat('tr-TR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(v)
      : v.toFixed(decimals);
    return `${prefix}${fmt}${suffix}`;
  });

  useEffect(() => {
    if (numericTo == null) return;
    const ctrl = animate(mv, numericTo, { duration: 1.4, ease: [0.2, 0.7, 0.3, 1], delay });
    return () => ctrl.stop();
  }, [numericTo, delay, mv]);

  useEffect(() => {
    if (ref.current && numericTo != null) {
      const u = display.on('change', (latest) => { if (ref.current) ref.current.textContent = latest; });
      return () => u();
    }
  }, [display, numericTo]);

  const sizeClass = size === 'xl' ? 'nc-xl' : size === 'm' ? 'nc-m' : '';

  return (
    <motion.div
      className="number-callout"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay, ease: [0.2, 0.7, 0.3, 1] }}
    >
      <div className="nc-label">{label}</div>
      <div className={`nc-value ${sizeClass}`}>
        {numericTo != null ? (
          <span className="numerals" ref={ref}>
            {prefix}
            {formatTr
              ? new Intl.NumberFormat('tr-TR', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(0)
              : (0).toFixed(decimals)
            }
            {suffix}
          </span>
        ) : highlight ? (
          <em>{value}</em>
        ) : (
          <>{value}</>
        )}
      </div>
      {foot && <div className="nc-foot">{foot}</div>}
    </motion.div>
  );
}
