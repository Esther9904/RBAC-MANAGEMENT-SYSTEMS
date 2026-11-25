import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { api } from '../api/client.js';

// "Actor" = the user we are currently acting as in the simulator.
const ActorContext = createContext(null);

export function ActorProvider({ children }) {
  const [users, setUsers] = useState([]);
  const [actorId, setActorId] = useState('');
  // Permissions are stored together with the user they belong to, so after a switch
  // we never mistake the previous user's permissions for the new user's.
  const [loaded, setLoaded] = useState({ actorId: '', permissions: [] });
  const [error, setError] = useState('');

  useEffect(() => {
    api
      .getDemoUsers()
      .then((list) => {
        setUsers(list);
        setActorId(list[0]?.id ?? ''); // start as the first user (Alice, the Admin)
      })
      .catch((err) => setError(err.message));
  }, []);

  // Whenever the acting user changes, ask the server what that user is allowed to do.
  useEffect(() => {
    if (!actorId) return undefined;
    let cancelled = false;
    api
      .getMe(actorId)
      .then((me) => {
        if (!cancelled) setLoaded({ actorId, permissions: me.permissions });
      })
      .catch((err) => {
        if (!cancelled) {
          setLoaded({ actorId, permissions: [] });
          setError(err.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [actorId]);

  const permissionsLoaded = loaded.actorId === actorId && actorId !== '';

  // UI hint only: the server re-checks every request, so this can never grant access.
  const can = useCallback(
    (permission) => permissionsLoaded && loaded.permissions.includes(permission),
    [permissionsLoaded, loaded],
  );

  const value = useMemo(
    () => ({ users, actorId, setActorId, permissionsLoaded, can, error }),
    [users, actorId, permissionsLoaded, can, error],
  );
  return <ActorContext.Provider value={value}>{children}</ActorContext.Provider>;
}

export function useActor() {
  const context = useContext(ActorContext);
  if (!context) throw new Error('useActor must be used inside <ActorProvider>');
  return context;
}