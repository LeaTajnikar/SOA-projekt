import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BookList = () => {
  const [books, setBooks] = useState([]);

  // Fetch knjig ob montaži komponente
  useEffect(() => {
    axios.get('http://books-service:8001/books')
      .then(response => setBooks(response.data))
      .catch(error => console.error('Error fetching books:', error));
  }, []);

  // Funkcija za brisanje knjige
  const handleDelete = (title) => {
    axios.delete(`http://books-service:8001/books/${title}`)
      .then(() => {
        alert('Book deleted!');
        setBooks(books.filter(book => book.title !== title));
      })
      .catch(error => console.error('Error deleting book:', error));
  };

  return (
    <div>
      <h2>Book List</h2>
      <ul>
        {books.map((book, index) => (
          <li key={index}>
            {book.title} by {book.author} ({book.genre})
            <button onClick={() => handleDelete(book.title)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BookList;
