
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await api.post(
        "/api/auth/login",
        formData
      );

      const { access_token, user } = response.data;

      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user", JSON.stringify(user));

      navigate("/dashboard");
    } catch (err) {
      console.error(err);

      const detail = err.response?.data?.detail;

      let message = "Unable to log in. Please try again.";

      if (typeof detail === "string") {
        message = detail;
      } else if (Array.isArray(detail)) {
        message = detail
          .map((item) => item.msg)
          .filter(Boolean)
          .join(", ");
      }

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-layout">
        <div className="login-welcome">
          <span className="login-welcome__eyebrow">
            YOUR PERSONAL LEARNING DESK
          </span>

          <h1>
            A little curiosity
            <br />
            goes a long way.
          </h1>

          <p className="login-welcome__description">
            Turn the videos you love into knowledge you can
            return to. Explore ideas, collect notes, and learn
            at your own pace.
          </p>

          <div
            className="login-art"
            aria-hidden="true"
          >
            <div className="login-art__sun" />
            <div className="login-art__page login-art__page--one" />
            <div className="login-art__page login-art__page--two" />
            <div className="login-art__line login-art__line--one" />
            <div className="login-art__line login-art__line--two" />
            <div className="login-art__line login-art__line--three" />
            <div className="login-art__book">
              <span />
              <span />
              <span />
            </div>
          </div>

          <p className="login-welcome__caption">
            Watch something. Understand something. Keep it.
          </p>
        </div>

        <div className="login-form-panel">
          <div className="login-form-panel__content">
            <span className="login-form-panel__eyebrow">
              YOUR LEARNING SPACE
            </span>

            <h2>Welcome back.</h2>

            <p className="login-form-panel__description">
              Sign in to continue where you left off.
            </p>

            <form
              className="auth-form"
              onSubmit={handleSubmit}
            >
              <div className="form-field">
                <label htmlFor="login-email">
                  Email address
                </label>

                <input
                  id="login-email"
                  type="email"
                  name="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  required
                />
              </div>

              <div className="form-field">
                <label htmlFor="login-password">
                  Password
                </label>

                <input
                  id="login-password"
                  type="password"
                  name="password"
                  autoComplete="current-password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter your password"
                  required
                />
              </div>

              {error && (
                <p className="form-error" role="alert">
                  {error}
                </p>
              )}

              <button
                className="button button--primary auth-form__submit"
                type="submit"
                disabled={loading}
              >
                {loading ? "Signing in..." : "Log in"}
              </button>

              <p className="login-signup-prompt">
                Haven't joined us yet?{" "}
                <Link to="/signup">Sign up</Link>
              </p>
            </form>
          </div>

          <p className="login-form-panel__footer">
            Make room for what matters.
          </p>
        </div>
      </section>
    </main>
  );
}

export default Login;
