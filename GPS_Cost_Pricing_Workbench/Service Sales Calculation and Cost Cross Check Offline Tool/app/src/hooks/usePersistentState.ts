import { useState, useEffect, useCallback } from 'react';

export function usePersistentState<T>(key: string, defaultValue: T): [T, (value: T | ((prev: T) => T)) => void, () => void] {
  // Initialize state from localStorage or fall back to default
  const [state, setState] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(key);
      if (stored) {
        return JSON.parse(stored) as T;
      }
    } catch (e) {
      console.warn(`Failed to parse localStorage key "${key}":`, e);
    }
    return defaultValue;
  });

  // Persist to localStorage whenever state changes
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch (e) {
      console.warn(`Failed to save localStorage key "${key}":`, e);
    }
  }, [key, state]);

  // Function to clear this specific key
  const clearKey = useCallback(() => {
    localStorage.removeItem(key);
    setState(defaultValue);
  }, [key, defaultValue]);

  return [state, setState, clearKey];
}
