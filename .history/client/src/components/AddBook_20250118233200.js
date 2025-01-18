import React, { useState } from 'react';
import axios from 'axios';

const AddBook = () => {
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [genre, setGenre] = useState('');

  // Funkcija za oddajo obrazca
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title || !author || !genre) {
      alert("All fields are required!");
      return;
    }

    const newBook = { title, author, genre };

    axios.post('http://books-service:8001/books', newBook)
      .then(() => {
        alert('Book added successfully!');
        setTitle('');
        setAuthor('');
        setGenre('');
      })
      .catch(error => console.error('Error adding book:', error));
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Add a New Book</h2>
      <div>
        <label>Title: </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Author: </label>
        <input
          type="text"
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Genre: </label>
        <input
          type="text"
          value={genre}
          onChange={(e) => setGenre(e.target.value)}
          required
        />
      </div>
      <button type="submit">Add Book</button>
    </form>
  );
};

export default AddBook;
