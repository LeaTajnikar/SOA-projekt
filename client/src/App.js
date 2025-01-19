import React, { useState } from 'react';
import './App.css';
import AddBook from './components/AddBook';
import BookList from './components/BookList';
import AddUser from './components/AddUser';
import UserList from './components/UserList';
import AddFeedback from './components/AddFeedback';
import FeedbackList from './components/FeedbackList';
import AddNotification from './components/AddNotification';
import NotificationList from './components/NotificationList';
import AddReservation from './components/AddReservation';
import ReservationList from './components/ReservationList';
import Login from './components/Login';
import Register from './components/Register';

const App = () => {
    const [token, setToken] = useState(null);

    const handleLogout = () => {
        setToken(null);
        alert("Odjava uspešna!");
    };

    return (
        <div>
            <h1>Library Management</h1>

            {!token ? (
                <div>
                    <h2>Prijava</h2>
                    <Login setToken={setToken} />
                    <h2>Registracija</h2>
                    <Register />
                </div>
            ) : (
                <div>
                    <button onClick={handleLogout}>Odjava</button>
                    <hr />
                    <AddBook />
                    <BookList />
                    <hr />
                    <AddUser />
                    <UserList />
                    <hr />
                    <AddFeedback />
                    <FeedbackList />
                    <hr />
                    <AddNotification />
                    <NotificationList />
                    <hr />
                    <AddReservation />
                    <ReservationList />
                    <hr />
                </div>
            )}
        </div>
    );
};

export default App;
