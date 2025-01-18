import React from 'react';
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
import StatistikaKomponenta from './components/StatistikaKomponenta';

const App = () => {
    return (
        <div>
            <h1>Library Management</h1>
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
            <StatistikaKomponenta />
        </div>
    );
};


export default App;
