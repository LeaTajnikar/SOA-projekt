import React, { useState } from 'react';
import axios from 'axios';

const AddFeedback = () => {
    const [username, setUsername] = useState('');
    const [message, setMessage] = useState('');
    const [rating, setRating] = useState('');

    const handleAddFeedback = () => {
        const newFeedback = { username, message, rating: Number(rating) };
        axios.post('http://feedback-service:8003/feedback', newFeedback)
            .then(() => {
                alert('Feedback added successfully!');
                setUsername('');
                setMessage('');
                setRating('');
            })
            .catch(error => console.error('Error adding feedback:', error));
    };

    return (
        <div>
            <h2>Add Feedback</h2>
            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <textarea
                placeholder="Your feedback"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
            />
            <input
                type="number"
                placeholder="Rating (1-5)"
                value={rating}
                onChange={(e) => setRating(e.target.value)}
            />
            <button onClick={handleAddFeedback}>Submit Feedback</button>
        </div>
    );
};

export default AddFeedback;
