import React, { useState, useEffect } from 'react';
import axios from 'axios';

const NotificationList = () => {
    const [notifications, setNotifications] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:8004/notifications')
            .then(response => setNotifications(response.data))
            .catch(error => console.error('Error fetching notifications:', error));
    }, []);

    return (
        <div>
            <h2>Notifications</h2>
            <ul>
                {notifications.map((notif, index) => (
                    <li key={index}>
                        <strong>{notif.title}</strong>: {notif.message} (User: {notif.user})
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default NotificationList;
