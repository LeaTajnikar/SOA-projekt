import React, { useState } from "react";
import axios from "axios";

const Login = ({ setToken }) => {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/token",
        new URLSearchParams({
          username: formData.username,
          password: formData.password,
        }),
        { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
      );
      const token = response.data.access_token;
      setToken(token);
      alert("Prijava uspešna!");
    } catch (error) {
      console.error("Napaka pri prijavi:", error.response.data);
      alert("Napaka pri prijavi: " + error.response.data.detail);
    }
  };

  return (
    <div>
      <h2>Prijava</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="username"
          placeholder="Uporabniško ime"
          value={formData.username}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Geslo"
          value={formData.password}
          onChange={handleChange}
          required
        />
        <button type="submit">Prijavi se</button>
      </form>
    </div>
  );
};

export default Login;
