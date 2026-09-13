import { TaskList } from "../../components/task-list";
export default function Page() {
  return (
    <>
      <section className="intro">
        <p className="eyebrow">SMALL STEPS, FORWARD</p>
        <h1>Tasks</h1>
        <p>A manageable little orbit. Try checking off a sample task.</p>
      </section>
      <section className="card">
        <h2>Your next steps</h2>
        <TaskList />
      </section>
    </>
  );
}
