import React, { useState } from 'react';
import axios from 'axios';

const AddNotification = () => {
    const [title, setTitle] = useState('');
    const [message, setMessage] = useState('');
    const [user, setUser] = useState('');

    const handleAddNotification = () => {
        const newNotification = { title, message, user };
        axios.post('http://notifications-service:8004/notifications', newNotification)
            .then(() => {
                alert('Notification added successfully!');
                setTitle('');
                setMessage('');
                setUser('');
            })
            .catch(error => console.error('Error adding notification:', error));
    };

    return (
        <div>
            <h2>Add Notification</h2>
            <input
                type="text"
                placeholder="Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
            />
            <textarea
                placeholder="Message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
            />
            <input
                type="text"
                placeholder="User"
                value={user}
                onChange={(e) => setUser(e.target.value)}
            />
            <button onClick={handleAddNotification}>Send Notification</button>
        </div>
    );
};

export default AddNotification;
