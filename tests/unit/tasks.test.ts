import { expect, test } from "vitest";
import { toggleTask } from "../../lib/tasks";
test("toggles only the selected task without mutating the input", () => {
  const tasks = [
    { id: "a", title: "Observe the moon", done: false },
    { id: "b", title: "Tea", done: false },
  ];
  expect(toggleTask(tasks, "a")).toEqual([
    { ...tasks[0], done: true },
    tasks[1],
  ]);
  expect(tasks[0].done).toBe(false);
});
