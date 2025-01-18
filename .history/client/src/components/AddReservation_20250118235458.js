import React, { useState } from 'react';
import axios from 'axios';

const AddReservation = () => {
    const [username, setUsername] = useState('');
    const [bookTitle, setBookTitle] = useState('');

    const handleAddReservation = () => {
        const newReservation = { username, book_title: bookTitle };
        axios.post('http://reservation-service:8005/reservations', newReservation)
            .then(response => {
                alert('Reservation added successfully!');
                setUsername('');
                setBookTitle('');
            })
            .catch(error => {
                if (error.response && error.response.data) {
                    alert(`Error: ${error.response.data.error}`);
                } else {
                    console.error('Error adding reservation:', error);
                }
            });
    };

    return (
        <div>
            <h2>Add Reservation</h2>
            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <input
                type="text"
                placeholder="Book Title"
                value={bookTitle}
                onChange={(e) => setBookTitle(e.target.value)}
            />
            <button onClick={handleAddReservation}>Add Reservation</button>
        </div>
    );
};

export default AddReservation;
