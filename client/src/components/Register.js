import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Register = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    role: "user",
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Posodobi URL z "http://"
      const response = await axios.post("http://localhost:8010/register", formData);

      alert("Registracija uspešna!");
      navigate("/"); // Preusmeritev na prijavno stran po registraciji
    } catch (error) {
      // Preveri, če obstaja `error.response`, da ne povzroči dodatnih napak
      const errorMessage = error.response?.data?.detail || "Napaka pri povezavi s strežnikom.";
      alert("Napaka pri registraciji: " + errorMessage);
    }
  };

  return (
    <div>
      <h2>Registracija</h2>
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
          type="email"
          name="email"
          placeholder="E-pošta"
          value={formData.email}
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
        <button type="submit">Registriraj se</button>
      </form>
      <button onClick={() => navigate("/")}>Nazaj na prijavo</button>
    </div>
  );
};

export default Register;
