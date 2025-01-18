import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ReservationList = () => {
    const [reservations, setReservations] = useState([]);

    // Pridobi rezervacije ob nalaganju komponente
    useEffect(() => {
        fetchReservations();
    }, []);

    // Funkcija za pridobivanje rezervacij iz mikrostoritve
    const fetchReservations = () => {
        axios.get('http://localhost:8005/reservations') // URL mikrostoritve
            .then(response => setReservations(response.data))
            .catch(error => console.error('Error fetching reservations:', error));
    };

    // Funkcija za podaljšanje rezervacije
    const handleExtendReservation = (username, bookTitle) => {
        axios.put(`http://localhost:8005/reservations/${username}/${bookTitle}/extend`)
            .then(response => {
                alert(`Reservation extended! New expiration date: ${response.data.new_expiration_date}`);
                fetchReservations(); // Osveži seznam rezervacij
            })
            .catch(error => {
                if (error.response && error.response.data) {
                    alert(`Error: ${error.response.data.error}`);
                } else {
                    console.error('Error extending reservation:', error);
                }
            });
    };

    // Funkcija za brisanje rezervacije
    const handleDeleteReservation = (username, bookTitle) => {
        axios.delete(`http://localhost:8005/reservations/${username}/${bookTitle}`)
            .then(() => {
                alert('Reservation deleted successfully');
                fetchReservations(); // Osveži seznam rezervacij
            })
            .catch(error => {
                if (error.response && error.response.data) {
                    alert(`Error: ${error.response.data.error}`);
                } else {
                    console.error('Error deleting reservation:', error);
                }
            });
    };

    return (
        <div>
            <h2>Reservations</h2>
            <ul>
                {reservations.map((res, index) => (
                    <li key={index}>
                        <strong>{res.book_title}</strong> reserved by {res.username} on {res.reservation_date} (expires on {res.expiration_date})
                        <button onClick={() => handleExtendReservation(res.username, res.book_title)} style={{ marginLeft: '10px' }}>
                            Extend
                        </button>
                        <button onClick={() => handleDeleteReservation(res.username, res.book_title)} style={{ marginLeft: '10px', color: 'red' }}>
                            Delete
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ReservationList;
