"use client";
import { useState } from "react";
import { useConvexAuth, useMutation, useQuery } from "convex/react";
import { api } from "../convex/_generated/api";
export function TaskList() {
  const { isAuthenticated, isLoading } = useConvexAuth();
  const tasks = useQuery(api.tasks.list, isAuthenticated ? {} : "skip");
  const add = useMutation(api.tasks.add);
  const toggle = useMutation(api.tasks.toggle);
  const remove = useMutation(api.tasks.remove);
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  async function save(action: () => Promise<unknown>) {
    setPending(true); setError("");
    try { await action(); } catch { setError("Could not save. Please try again; your change has not been confirmed."); }
    finally { setPending(false); }
  }
  if (isLoading) return <p role="status">Connecting securely…</p>;
  if (!isAuthenticated) return <p role="alert">Authentication unavailable. Sign in again or check the Convex authentication configuration.</p>;
  if (tasks === undefined) return <p role="status">Loading saved tasks…</p>;
  return <div className="task-list">
    <form onSubmit={event => { event.preventDefault(); void save(async () => { await add({ title }); setTitle(""); }); }}>
      <label htmlFor="task-title">New task</label>{" "}
      <input id="task-title" value={title} onChange={e => setTitle(e.target.value)} maxLength={500} required disabled={pending} />{" "}
      <button type="submit" disabled={pending || !title.trim()}>Add task</button>
    </form>
    {error && <p role="alert">{error}</p>}
    {tasks.length === 0 && <p>No tasks yet. Add your first task.</p>}
    {tasks.map(task => <div className={task.done ? "task done" : "task"} key={task._id}>
      <label><input type="checkbox" checked={task.done} disabled={pending} onChange={() => void save(() => toggle({ id: task._id }))} /> {task.title}</label>
      <button disabled={pending} aria-label={`Delete ${task.title}`} onClick={() => void save(() => remove({ id: task._id }))}>Delete</button>
    </div>)}
    <p className="subtle">{tasks.filter(t => t.done).length} of {tasks.length} complete</p>
  </div>;
}
