
import { Link, useLocation, useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem("access_token");

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    navigate("/login", { replace: true });
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="site-header">
      <nav className="app-nav" aria-label="Main navigation">
        <Link
          to={token ? "/dashboard" : "/"}
          className="app-nav__brand"
          aria-label="LearnTube AI home"
        >
          LearnTube <span>AI</span>
        </Link>

        <div className="app-nav__links">
          {token ? (
            <>
              <Link
                to="/dashboard"
                className={`app-nav__link ${
                  isActive("/dashboard")
                    ? "app-nav__link--active"
                    : ""
                }`}
                aria-current={
                  isActive("/dashboard") ? "page" : undefined
                }
              >
                Dashboard
              </Link>

              <button
                type="button"
                className="button button--secondary"
                onClick={handleLogout}
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className={`app-nav__link ${
                  isActive("/login")
                    ? "app-nav__link--active"
                    : ""
                }`}
                aria-current={
                  isActive("/login") ? "page" : undefined
                }
              >
                Log in
              </Link>

              <Link
                to="/signup"
                className={`app-nav__link app-nav__link--signup ${
                  isActive("/signup")
                    ? "app-nav__link--active"
                    : ""
                }`}
                aria-current={
                  isActive("/signup") ? "page" : undefined
                }
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}

export default Navbar;
