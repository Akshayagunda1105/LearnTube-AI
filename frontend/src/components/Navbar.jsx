
import { Link, useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    navigate("/login", { replace: true });
  };

  return (
    <nav
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "16px 24px",
        borderBottom: "1px solid #ccc",
        gap: "16px",
        flexWrap: "wrap",
      }}
    >
      <Link
        to={token ? "/dashboard" : "/"}
        style={{
          fontSize: "1.3rem",
          fontWeight: "bold",
          textDecoration: "none",
        }}
      >
        LearnTube AI
      </Link>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "16px",
        }}
      >
        {token ? (
          <>
            <Link to="/dashboard">Dashboard</Link>

            <button type="button" onClick={handleLogout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/signup">Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
