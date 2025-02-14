import { useRef } from 'react';

export function useClientOnce(fn: () => void): void {
  const canCall = useRef(true);
  console.log("useClientOnce", fn, canCall.current);
  if (typeof window !== 'undefined' && canCall.current) {
    canCall.current = false;
    fn();
  }
}
