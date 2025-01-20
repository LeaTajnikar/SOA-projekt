import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Login = ({ setToken }) => {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:8010/token",
        new URLSearchParams({
          username: formData.username,
          password: formData.password,
        }),
        { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
      );

      if (response && response.data.access_token) {
        const token = response.data.access_token;
        setToken(token);
        alert("Prijava uspešna!");
        navigate("/home"); // Preusmeritev na nadzorno ploščo po prijavi
      } else {
        throw new Error("Prijava ni uspela. Preverite vaše podatke.");
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || "Napaka pri povezavi s strežnikom.";
      alert("Napaka pri prijavi: " + errorMessage);
      console.error("Napaka pri prijavi:", error);
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
      <button onClick={() => navigate("/register")}>Registracija</button>
    </div>
  );
};

export default Login;
