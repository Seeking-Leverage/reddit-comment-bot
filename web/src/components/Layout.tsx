import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "Generator" },
  { to: "/brand", label: "Brand Profile" },
  { to: "/playbooks", label: "Playbooks" },
  { to: "/history", label: "History" },
  { to: "/tracker", label: "Tracker" },
];

export default function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>Reddit Console</h1>
        <nav>
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}