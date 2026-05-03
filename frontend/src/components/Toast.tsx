import { createContext, useCallback, useContext, useState, type ReactNode } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

type Kind = 'info' | 'ok' | 'error';
interface ToastItem { id: number; msg: string; kind: Kind; }
interface ToastCtx { push: (msg: string, kind?: Kind, ttl?: number) => void; }

const Ctx = createContext<ToastCtx | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);

  const push = useCallback((msg: string, kind: Kind = 'info', ttl = 3500) => {
    const id = Date.now() + Math.random();
    setItems(s => [...s, { id, msg, kind }]);
    setTimeout(() => setItems(s => s.filter(i => i.id !== id)), ttl);
  }, []);

  return (
    <Ctx.Provider value={{ push }}>
      {children}
      <div className="toast-stack">
        <AnimatePresence>
          {items.map(t => (
            <motion.div
              key={t.id}
              className={`toast ${t.kind}`}
              initial={{ opacity: 0, y: 18, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: 30 }}
              transition={{ duration: 0.28, ease: [0.2, 0.7, 0.3, 1] }}
            >
              {t.msg}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </Ctx.Provider>
  );
}

export function useToast() {
  const c = useContext(Ctx);
  if (!c) throw new Error('useToast requires ToastProvider');
  return c;
}
