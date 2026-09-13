"use client";
import { useState } from "react";
import { toggleTask } from "../lib/tasks";
const initial = [
  { id: "idea", title: "Make room for a small idea", done: false },
  { id: "walk", title: "Take a walk, notice the sky", done: false },
  { id: "desk", title: "Give your desk a fresh start", done: true },
];
export function TaskList() {
  const [tasks, setTasks] = useState(initial);
  return (
    <div className="task-list">
      {tasks.map((task, index) => (
        <label className={task.done ? "task done" : "task"} key={task.id}>
          <input
            type="checkbox"
            checked={task.done}
            onChange={() => setTasks(toggleTask(tasks, task.id))}
          />
          <span>{task.title}</span>
          <small>{["Creative", "Recharge", "Personal"][index]}</small>
        </label>
      ))}
      <p className="subtle">
        {tasks.filter((t) => t.done).length} of {tasks.length} complete · one
        small step at a time
      </p>
    </div>
  );
}
