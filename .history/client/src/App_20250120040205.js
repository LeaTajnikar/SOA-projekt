import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
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

// API Call Wrapper
const apiCall = async (url, options, setToken) => {
    try {
        const response = await fetch(url, options);
        if (response.status === 401) {
            // Handle 401 - Redirect to login
            setToken(null);
            alert('Session expired. Please log in again.');
            return { redirectToLogin: true };
        }
        return await response.json();
    } catch (error) {
        console.error('API call error:', error);
        return { error };
    }
};

const ProtectedRoute = ({ token, children }) => {
    return token ? children : <Navigate to="/" />;
};

const App = () => {
    const [token, setToken] = useState(null);

    const handleLogout = () => {
        setToken(null);
        alert('Odjava uspešna!');
    };

    return (
        <Router>
            <div>
                <h1>Library Management</h1>
                <Routes>
               
                    <Route
                        path="/"
                        element={!token ? <Login setToken={setToken} /> : <Navigate to="/dashboard" />}
                    />

                    <Route path="/register" element={<Register />} />

                
                    <Route
                        path="/dashboard"
                        element={
                            <ProtectedRoute token={token}>
                                <div>
                                    <button onClick={handleLogout}>Odjava</button>
                                    <hr />
                                    <AddBook apiCall={apiCall} token={token} setToken={setToken} />
                                    <BookList apiCall={apiCall} token={token} setToken={setToken} />
                                    <hr />
                                    <AddUser apiCall={apiCall} token={token} setToken={setToken} />
                                    <UserList apiCall={apiCall} token={token} setToken={setToken} />
                                    <hr />
                                    <AddFeedback apiCall={apiCall} token={token} setToken={setToken} />
                                    <FeedbackList apiCall={apiCall} token={token} setToken={setToken} />
                                    <hr />
                                    <AddNotification apiCall={apiCall} token={token} setToken={setToken} />
                                    <NotificationList apiCall={apiCall} token={token} setToken={setToken} />
                                    <hr />
                                    <AddReservation apiCall={apiCall} token={token} setToken={setToken} />
                                    <ReservationList apiCall={apiCall} token={token} setToken={setToken} />
                                </div>
                            </ProtectedRoute>
                        }
                    />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
