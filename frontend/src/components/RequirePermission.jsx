import { useActor } from '../context/ActorContext.jsx';

// Shows its children only if the acting user holds `permission`.
// This avoids requests we already know the server will refuse. It is a UI courtesy,
// not security: the server checks every request regardless.
export default function RequirePermission({ permission, children }) {
  const { can, permissionsLoaded } = useActor();

  if (!permissionsLoaded) return <p className="muted">Loading…</p>;
  if (!can(permission)) {
    return (
      <p className="notice notice-neutral">
        This user does not have the <code>{permission}</code> permission, so this section is not requested. Switch
        to a user who has it. The server would refuse the request anyway.
      </p>
    );
  }
  return children;
}