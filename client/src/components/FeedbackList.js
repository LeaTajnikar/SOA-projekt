import React, { useState, useEffect } from 'react';
import axios from 'axios';

const FeedbackList = () => {
    const [feedback, setFeedback] = useState([]);

    useEffect(() => {
        axios.get('http://localhost:8003/feedback')
            .then(response => setFeedback(response.data))
            .catch(error => console.error('Error fetching feedback:', error));
    }, []);

    return (
        <div>
            <h2>Feedback List</h2>
            <ul>
                {feedback.map((fb, index) => (
                    <li key={index}>
                        {fb.username}: {fb.message} (Rating: {fb.rating})
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default FeedbackList;
