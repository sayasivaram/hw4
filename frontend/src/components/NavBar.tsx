import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import CrestMark from "./CrestMark";
import "./NavBar.css";

const LINKS = [
  { to: "/", label: "Home", end: true },
  { to: "/products", label: "Products" },
  { to: "/about", label: "About Us" },
];

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  function handleLogout() {
    logout();
    setMobileOpen(false);
    navigate("/");
  }

  function closeMobileMenu() {
    setMobileOpen(false);
  }

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <NavLink to="/" className="navbar-brand" onClick={closeMobileMenu}>
          <CrestMark className="navbar-brand-mark" letter="C" />
          <span>
            Campus Customs
            <small>New Haven, Connecticut</small>
          </span>
        </NavLink>

        <nav className="navbar-links">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => (isActive ? "navbar-link active" : "navbar-link")}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="navbar-actions">
          {user ? (
            <>
              <span className="navbar-greeting">Hi, {user.first_name ?? user.email}</span>
              <button className="btn btn-outline" onClick={handleLogout}>
                Log Out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="btn btn-outline">
                Log In
              </NavLink>
              <NavLink to="/create-account" className="btn btn-primary">
                Create Account
              </NavLink>
            </>
          )}
        </div>

        <button
          className="navbar-menu-toggle"
          onClick={() => setMobileOpen((v) => !v)}
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen}
        >
          <span />
          <span />
          <span />
        </button>
      </div>

      {mobileOpen && (
        <div className="navbar-mobile-menu">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => (isActive ? "navbar-link active" : "navbar-link")}
              onClick={closeMobileMenu}
            >
              {link.label}
            </NavLink>
          ))}
          <hr className="navbar-mobile-divider" />
          {user ? (
            <>
              <span className="navbar-greeting">Hi, {user.first_name ?? user.email}</span>
              <button className="btn btn-outline" onClick={handleLogout}>
                Log Out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="btn btn-outline" onClick={closeMobileMenu}>
                Log In
              </NavLink>
              <NavLink to="/create-account" className="btn btn-primary" onClick={closeMobileMenu}>
                Create Account
              </NavLink>
            </>
          )}
        </div>
      )}
    </header>
  );
}
