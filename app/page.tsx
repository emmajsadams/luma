import Link from "next/link";
import { ArrowUpRight, Sparkles, Moon, Coffee } from "lucide-react";
import { TaskList } from "../components/task-list";
export default function Page() {
  return (
    <>
      <section className="intro">
        <p className="eyebrow">WELCOME TO YOUR ORBIT</p>
        <h1>A little space to focus.</h1>
        <p>
          Gather your thoughts. Find your rhythm. Make room for what matters.
        </p>
      </section>
      <section className="hero">
        <div>
          <span className="pill">
            <Sparkles size={14} aria-hidden="true" /> A GENTLER KIND OF
            PRODUCTIVITY
          </span>
          <h2>
            Big dreams.
            <br />
            Small, steady steps.
          </h2>
          <p>
            Your everyday mission control, with a little more breathing room.
          </p>
          <Link className="button" href="/tasks">
            Find your next step <ArrowUpRight size={17} aria-hidden="true" />
          </Link>
        </div>
        <div className="planet-scene" aria-hidden="true">
          <div className="orbit-ring" />
          <div className="planet" />
          <span className="star s1">✦</span>
          <span className="star s2">✧</span>
          <span className="tiny-moon" />
          <span className="scene-label">TAKE IT AT YOUR OWN PACE</span>
        </div>
      </section>
      <div className="dashboard-grid">
        <section className="card tasks-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">ONE THING AT A TIME</p>
              <h2>In your orbit</h2>
            </div>
            <Link href="/tasks" aria-label="View all tasks">
              <ArrowUpRight aria-hidden="true" />
            </Link>
          </div>
          <TaskList />
        </section>
        <section className="card note-card">
          <NotebookHeader />
          <p className="note-script">
            What if there’s a little more wonder in the ordinary?
          </p>
          <p className="subtle">
            A sample thought, waiting to become something.
          </p>
          <Link className="text-link" href="/notes">
            Explore your notes <ArrowUpRight size={16} aria-hidden="true" />
          </Link>
        </section>
        <section className="card rhythm">
          <Coffee aria-hidden="true" />
          <div>
            <h2>A moment for yourself</h2>
            <p>Unclench your jaw. Let your shoulders drop. You’re here.</p>
          </div>
          <Moon aria-hidden="true" />
        </section>
      </div>
    </>
  );
}
function NotebookHeader() {
  return <p className="eyebrow">✧ FROM THE IDEA GARDEN</p>;
}
