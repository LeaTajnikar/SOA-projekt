import React, { useState } from 'react';
import axios from 'axios';

const AddUser = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');

    const handleAddUser = () => {
        const newUser = { username, email };
        axios.post('http://users-service:8002/users', newUser)
            .then(() => {
                alert('User added successfully!');
                setUsername('');
                setEmail('');
            })
            .catch(error => console.error('Error adding user:', error));
    };

    return (
        <div>
            <h2>Add a New User</h2>
            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />
            <button onClick={handleAddUser}>Add User</button>
        </div>
    );
};

export default AddUser;
