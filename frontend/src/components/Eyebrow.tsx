import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  tone?: 'default' | 'tuff';
  rule?: boolean;
  className?: string;
}

export function Eyebrow({ children, tone = 'default', rule = true, className = '' }: Props) {
  return (
    <span className={`eyebrow ${tone === 'tuff' ? 'tuff' : ''} ${rule ? 'with-rule' : ''} ${className}`}>
      {children}
    </span>
  );
}
