
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function Signup() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

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
    setSuccess("");

    try {
      await api.post("/api/auth/signup", formData);

      setSuccess("Your account has been created. You can now log in.");

      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1000);
    } catch (err) {
      console.error(err);

      const detail = err.response?.data?.detail;

      if (typeof detail === "string") {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(
          detail.map((item) => item.msg).filter(Boolean).join(", ")
        );
      } else {
        setError("Unable to create your account. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <div className="login-layout">
        <section className="login-welcome">
          <span className="login-welcome__eyebrow">
            YOUR PERSONAL LEARNING DESK
          </span>

          <h1>
            Start with a
            <br />
            little curiosity.
          </h1>

          <p className="login-welcome__description">
            Build a learning space of your own. Turn videos into
            useful notes, revisit important ideas, and keep learning
            at your own pace.
          </p>

          <div className="login-art" aria-hidden="true">
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
        </section>

        <section className="login-form-panel">
          <div className="login-form-panel__content">
            <span className="login-form-panel__eyebrow">
              YOUR LEARNING SPACE
            </span>

            <h2>Create your account.</h2>

            <p className="login-form-panel__description">
              A good place to begin your next learning journey.
            </p>

            <form className="auth-form" onSubmit={handleSubmit}>
              <div className="form-field">
                <label htmlFor="signup-name">Name</label>
                <input
                  id="signup-name"
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Your name"
                  autoComplete="name"
                  required
                />
              </div>

              <div className="form-field">
                <label htmlFor="signup-email">Email address</label>
                <input
                  id="signup-email"
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  autoComplete="email"
                  required
                />
              </div>

              <div className="form-field">
                <label htmlFor="signup-password">Password</label>
                <input
                  id="signup-password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="At least 8 characters"
                  autoComplete="new-password"
                  minLength={8}
                  required
                />
              </div>

              <button
                className="button button--primary auth-form__submit"
                type="submit"
                disabled={loading}
              >
                {loading ? "Creating account..." : "Create account"}
              </button>
            </form>

            {error && (
              <p className="form-message form-message--error" role="alert">
                {error}
              </p>
            )}

            {success && (
              <p
                className="form-message form-message--success"
                role="status"
              >
                {success}
              </p>
            )}

            <p className="login-signup-prompt">
              Already have an account? <Link to="/login">Log in</Link>
            </p>

            <p className="login-form-panel__footer">
              Make room for what matters.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}

export default Signup;
