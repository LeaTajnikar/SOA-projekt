import React, { useState } from "react";
import axios from "axios";

const Register = () => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    role: "user", // privzeta vloga
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:8000/register", formData);
      alert("Registracija uspešna!");
    } catch (error) {
      console.error("Napaka pri registraciji:", error.response.data);
      alert("Napaka pri registraciji: " + error.response.data.detail);
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
    </div>
  );
};

export default Register;
