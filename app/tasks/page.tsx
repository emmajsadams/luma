import { TaskList } from "../../components/task-list";
import { auth } from "@clerk/nextjs/server";
import { setupAvailable } from "../../lib/setup";
export default async function Page() {
  if (!setupAvailable()) return null;
  await auth.protect();
  return (
    <>
      <section className="intro">
        <p className="eyebrow">SMALL STEPS, FORWARD</p>
        <h1>Tasks</h1>
        <p>Your tasks, saved to your account.</p>
      </section>
      <section className="card">
        <h2>Your next steps</h2>
        <TaskList />
      </section>
    </>
  );
}
