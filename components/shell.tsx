"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Orbit,
  LayoutDashboard,
  CircleCheck,
  NotebookPen,
  CalendarDays,
  Sparkles,
} from "lucide-react";
const links = [
  { href: "/", title: "Overview", icon: LayoutDashboard },
  { href: "/tasks", title: "Tasks", icon: CircleCheck },
  { href: "/notes", title: "Notes", icon: NotebookPen },
  { href: "/calendar", title: "Calendar", icon: CalendarDays },
];
export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  return (
    <div className="workspace">
      <a className="skip" href="#main">
        Skip to content
      </a>
      <aside className="sidebar">
        <Link href="/" className="brand" aria-label="Luma home">
          <Orbit aria-hidden="true" />
          luma<span>✦</span>
        </Link>
        <p className="eyebrow nav-label">YOUR LITTLE UNIVERSE</p>
        <nav aria-label="Main navigation">
          {links.map(({ href, title, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              aria-current={path === href ? "page" : undefined}
            >
              <Icon size={19} aria-hidden="true" />
              <span>{title}</span>
            </Link>
          ))}
        </nav>
        <div className="side-note">
          <Sparkles aria-hidden="true" />
          <p>
            Small steps.
            <br />
            Wonderful places.
          </p>
          <span>You don’t have to do it all today.</span>
        </div>
        <div className="profile">
          <span className="avatar">L</span>
          <div>
            Little explorer<small>Personal demo space</small>
          </div>
        </div>
      </aside>
      <div className="content">
        <header className="topbar">
          <span>
            Personal space <span aria-hidden="true">/</span>{" "}
            <strong>
              {links.find((l) => l.href === path)?.title ?? "Luma"}
            </strong>
          </span>
          <span className="status">
            <i />
            LOCAL DEMO
          </span>
        </header>
        <main id="main" tabIndex={-1}>
          {children}
        </main>
        <footer>
          Demo workspace · changes last until refresh
          <span>No account, cloud sync, or backend connected.</span>
        </footer>
      </div>
    </div>
  );
}
