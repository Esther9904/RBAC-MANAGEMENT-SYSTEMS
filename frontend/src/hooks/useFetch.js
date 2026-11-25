import { useCallback, useEffect, useState } from 'react';

// Runs `loader` (a function returning a promise) and tracks loading / data / error.
// It re-runs whenever a value in `deps` changes, or when reload() is called.
export function useFetch(loader, deps) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  const [reloadCount, setReloadCount] = useState(0);

  useEffect(() => {
    let cancelled = false; // ignore answers that arrive after we moved on (e.g. user switched)
    setState((previous) => ({ ...previous, loading: true, error: null }));

    loader()
      .then((data) => {
        if (!cancelled) setState({ data, error: null, loading: false });
      })
      .catch((error) => {
        if (!cancelled) setState({ data: null, error, loading: false });
      });

    return () => {
      cancelled = true;
    };
  }, [...deps, reloadCount]);

  const reload = useCallback(() => setReloadCount((count) => count + 1), []);
  return { ...state, reload };
}