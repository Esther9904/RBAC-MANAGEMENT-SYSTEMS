import { useActor } from '../context/ActorContext.jsx';

export default function UserSwitcher() {
  const { users, actorId, setActorId } = useActor();

  return (
    <div className="switcher">
      <label htmlFor="actor-select">Acting as</label>
      <select id="actor-select" value={actorId} onChange={(event) => setActorId(event.target.value)}>
        {users.map((user) => (
          <option key={user.id} value={user.id}>
            {user.name}
          </option>
        ))}
      </select>
    </div>
  );
}