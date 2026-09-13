export type Task = { id: string; title: string; done: boolean };
export function toggleTask(tasks: Task[], id: string): Task[] {
  return tasks.map((task) =>
    task.id === id ? { ...task, done: !task.done } : task,
  );
}
