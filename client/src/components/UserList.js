import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserList = () => {
    const [users, setUsers] = useState([]);

    useEffect(() => {
        // Pridobi seznam uporabnikov iz mikrostoritve
        axios.get('http://localhost:8002/users')
            .then(response => setUsers(response.data))
            .catch(error => console.error('Error fetching users:', error));
    }, []);

    return (
        <div>
            <h2>User List</h2>
            <ul>
                {users.map((user, index) => (
                    <li key={index}>{user.username} ({user.email})</li>
                ))}
            </ul>
        </div>
    );
};

export default UserList;
