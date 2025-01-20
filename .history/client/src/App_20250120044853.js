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
import Recommendations from './components/Register'

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
                    {/* Prijava kot privzeta stran */}
                    <Route
                        path="/"
                        element={!token ? <Login setToken={setToken} /> : <Navigate to="/dashboard" />}
                    />

                    {/* Registracija */}
                    <Route path="/register" element={<Register />} />

                    {/* Nadzorna plošča (zaščitena vsebina) */}
                    <Route
                        path="/dashboard"
                        element={
                            <ProtectedRoute token={token}>
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
                                    <Recommendations />
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
