import React, { useState, useEffect } from 'react';
import { Edit, Trash2, PlusCircle, MessageSquare, UserPlus, LogIn, LogOut, XCircle, CheckCircle } from 'lucide-react'; // Import Lucide icons

// Main App component
const App = () => {
    // State variables for managing patient data and UI
    const [patients, setPatients] = useState([]);
    const [newPatient, setNewPatient] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
        date_of_birth: '',
        address: '',
        gender: ''
    });
    const [editingPatient, setEditingPatient] = useState(null); // Stores patient being edited
    const [chatbotQuery, setChatbotQuery] = useState(''); // Input for chatbot
    const [chatbotResponse, setChatbotResponse] = useState(''); // Output from chatbot
    const [loading, setLoading] = useState(false); // Loading state for API calls
    const [error, setError] = useState(''); // Error message state
    const [successMessage, setSuccessMessage] = useState(''); // Success message state

    // Authentication states
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('patient'); // Default role for registration
    const [token, setToken] = useState(localStorage.getItem('hms_access_token') || '');
    const [currentUser, setCurrentUser] = useState(null); // Stores authenticated user info

    // Base URL for your FastAPI backend
    const API_BASE_URL = 'http://127.0.0.1:8000';

    // Headers for authenticated requests
    const getAuthHeaders = () => {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        };
    };

    // Effect to fetch patients when component mounts or token changes
    useEffect(() => {
        if (token) {
            fetchCurrentUser(); // Fetch current user details if token exists
            fetchPatients();
        }
    }, [token]); // Re-run when token changes

    // Function to fetch current authenticated user details
    const fetchCurrentUser = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await fetch(`${API_BASE_URL}/users/me/`, {
                method: 'GET',
                headers: getAuthHeaders(),
            });
            if (!response.ok) {
                // If token is invalid or expired, log out
                handleLogout();
                throw new Error(`Authentication failed. Please log in again.`);
            }
            const data = await response.json();
            setCurrentUser(data);
        } catch (err) {
            setError(`Failed to fetch user: ${err.message}`);
            console.error('Error fetching current user:', err);
            handleLogout(); // Ensure logout if current user fetch fails
        } finally {
            setLoading(false);
        }
    };

    // Function to fetch patients from the backend
    const fetchPatients = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await fetch(`${API_BASE_URL}/patients/`, {
                method: 'GET',
                headers: getAuthHeaders(),
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setPatients(data);
        } catch (err) {
            setError(`Failed to fetch patients: ${err.message}`);
            console.error('Error fetching patients:', err);
        } finally {
            setLoading(false);
        }
    };

    // Handle input changes for new patient form
    const handleNewPatientChange = (e) => {
        const { name, value } = e.target;
        setNewPatient(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    // Handle input changes for editing patient form
    const handleEditPatientChange = (e) => {
        const { name, value } = e.target;
        setEditingPatient(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    // Function to add a new patient
    const addPatient = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccessMessage('');
        try {
            const response = await fetch(`${API_BASE_URL}/patients/`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(newPatient),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error! status: ${response.status}, Detail: ${errorData.detail || 'Unknown error'}`);
            }
            // Clear form and re-fetch patients to update the list
            setNewPatient({
                first_name: '',
                last_name: '',
                email: '',
                phone_number: '',
                date_of_birth: '',
                address: '',
                gender: ''
            });
            fetchPatients();
            setSuccessMessage('Patient added successfully!');
        } catch (err) {
            setError(`Failed to add patient: ${err.message}`);
            console.error('Error adding patient:', err);
        } finally {
            setLoading(false);
        }
    };

    // Function to start editing a patient
    const startEditPatient = (patient) => {
        setEditingPatient({ ...patient }); // Create a copy to edit
    };

    // Function to update an existing patient
    const updatePatient = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccessMessage('');
        if (!editingPatient || !editingPatient.id) {
            setError("No patient selected for update.");
            setLoading(false);
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/patients/${editingPatient.id}`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify(editingPatient),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error! status: ${response.status}, Detail: ${errorData.detail || 'Unknown error'}`);
            }
            setEditingPatient(null); // Exit edit mode
            fetchPatients(); // Re-fetch patients to update the list
            setSuccessMessage('Patient updated successfully!');
        } catch (err) {
            setError(`Failed to update patient: ${err.message}`);
            console.error('Error updating patient:', err);
        } finally {
            setLoading(false);
        }
    };

    // Function to delete a patient
    const deletePatient = async (id) => {
        setLoading(true);
        setError('');
        setSuccessMessage('');
        try {
            const response = await fetch(`${API_BASE_URL}/patients/${id}`, {
                method: 'DELETE',
                headers: getAuthHeaders(),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error! status: ${response.status}, Detail: ${errorData.detail || 'Unknown error'}`);
            }
            fetchPatients(); // Re-fetch patients to update the list
            setSuccessMessage('Patient deleted successfully!');
        } catch (err) {
            setError(`Failed to delete patient: ${err.message}`);
            console.error('Error deleting patient:', err);
        } finally {
            setLoading(false);
        }
    };

    // Function to send query to chatbot
    const sendChatbotQuery = async (e) => {
        e.preventDefault();
        setLoading(true);
        setChatbotResponse('');
        setError('');
        try {
            const response = await fetch(`${API_BASE_URL}/chatbot/query`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    query: chatbotQuery,
                }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error! status: ${response.status}, Detail: ${errorData.detail || 'Unknown error'}`);
            }
            const data = await response.json();
            setChatbotResponse(data.response);
            setChatbotQuery(''); // Clear chatbot input
        } catch (err) {
            setError(`Chatbot query failed: ${err.message}`);
            console.error('Error sending chatbot query:', err);
        } finally {
            setLoading(false);
        }
    };

    // --- Authentication Functions ---
    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccessMessage('');
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${API_BASE_URL}/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString(),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Login failed: ${errorData.detail || 'Invalid credentials'}`);
            }

            const data = await response.json();
            localStorage.setItem('hms_access_token', data.access_token);
            setToken(data.access_token);
            setSuccessMessage('Logged in successfully!');
            setUsername('');
            setPassword('');
            fetchCurrentUser(); // Fetch user details after login
        } catch (err) {
            setError(err.message);
            console.error('Login error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccessMessage('');
        try {
            const response = await fetch(`${API_BASE_URL}/users/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password, role }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Registration failed: ${errorData.detail || 'Unknown error'}`);
            }

            setSuccessMessage(`User "${username}" registered as "${role}" successfully!`);
            setUsername('');
            setPassword('');
            setRole('patient'); // Reset role to default
        } catch (err) {
            setError(err.message);
            console.error('Registration error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('hms_access_token');
        setToken('');
        setCurrentUser(null);
        setPatients([]); // Clear patient data on logout
        setSuccessMessage('Logged out successfully.');
        setError('');
    };

    // Helper to check user roles for conditional rendering
    const hasRole = (roles) => {
        if (!currentUser) return false;
        if (Array.isArray(roles)) {
            return roles.some(r => currentUser.role === r);
        }
        return currentUser.role === roles;
    };


    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 font-inter flex flex-col items-center">
            {/* Tailwind CSS CDN */}
            <script src="https://cdn.tailwindcss.com"></script>
            {/* Inter Font */}
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
            <style>
                {`
                body {
                    font-family: 'Inter', sans-serif;
                }
                input, select, textarea {
                    @apply focus:ring-blue-500 focus:border-blue-500;
                }
                `}
            </style>

            <h1 className="text-5xl font-extrabold text-blue-800 mb-10 rounded-xl p-5 bg-white shadow-2xl transform hover:scale-105 transition-transform duration-300 ease-in-out">
                🏥 Hospital Management System
            </h1>

            {loading && (
                <div className="fixed inset-0 bg-gray-800 bg-opacity-60 flex items-center justify-center z-50 backdrop-blur-sm">
                    <div className="bg-white p-6 rounded-lg shadow-xl flex items-center animate-pulse">
                        <svg className="animate-spin h-7 w-7 text-blue-600 mr-3" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span className="text-lg font-medium text-gray-700">Loading...</span>
                    </div>
                </div>
            )}

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg relative mb-8 w-full max-w-3xl shadow-md flex items-center justify-between animate-fade-in">
                    <div className="flex items-center">
                        <XCircle className="w-6 h-6 mr-3" />
                        <strong className="font-bold mr-2">Error:</strong>
                        <span className="block sm:inline">{error}</span>
                    </div>
                    <button onClick={() => setError('')} className="text-red-500 hover:text-red-700 focus:outline-none">
                        <XCircle className="w-5 h-5" />
                    </button>
                </div>
            )}

            {successMessage && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-6 py-4 rounded-lg relative mb-8 w-full max-w-3xl shadow-md flex items-center justify-between animate-fade-in">
                    <div className="flex items-center">
                        <CheckCircle className="w-6 h-6 mr-3" />
                        <strong className="font-bold mr-2">Success:</strong>
                        <span className="block sm:inline">{successMessage}</span>
                    </div>
                    <button onClick={() => setSuccessMessage('')} className="text-green-500 hover:text-green-700 focus:outline-none">
                        <XCircle className="w-5 h-5" />
                    </button>
                </div>
            )}

            {/* Authentication Section */}
            <div className="bg-white p-8 rounded-xl shadow-xl w-full max-w-2xl mb-8 border border-blue-200">
                <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
                    {currentUser ? `Welcome, ${currentUser.username} (${currentUser.role})` : 'Login / Register'}
                </h2>
                {!token ? (
                    <div className="flex flex-col md:flex-row gap-8">
                        {/* Login Form */}
                        <form onSubmit={handleLogin} className="flex-1 space-y-4 p-4 border border-gray-200 rounded-lg shadow-sm bg-gray-50">
                            <h3 className="text-xl font-semibold text-gray-700 mb-4 flex items-center"><LogIn className="mr-2" /> Login</h3>
                            <input
                                type="text"
                                placeholder="Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-200"
                            />
                            <input
                                type="password"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-200"
                            />
                            <button
                                type="submit"
                                className="w-full bg-blue-600 text-white p-3 rounded-md hover:bg-blue-700 transition duration-300 ease-in-out font-semibold shadow-md flex items-center justify-center"
                            >
                                <LogIn className="mr-2" size={20} /> Login
                            </button>
                        </form>

                        {/* Register Form */}
                        <form onSubmit={handleRegister} className="flex-1 space-y-4 p-4 border border-gray-200 rounded-lg shadow-sm bg-gray-50">
                            <h3 className="text-xl font-semibold text-gray-700 mb-4 flex items-center"><UserPlus className="mr-2" /> Register New User</h3>
                            <input
                                type="text"
                                placeholder="New Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-200"
                            />
                            <input
                                type="password"
                                placeholder="New Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-200"
                            />
                            <select
                                value={role}
                                onChange={(e) => setRole(e.target.value)}
                                className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 transition duration-200"
                            >
                                <option value="patient">Patient</option>
                                <option value="doctor">Doctor</option>
                                <option value="nurse">Nurse</option>
                                <option value="receptionist">Receptionist</option>
                                <option value="pharmacist">Pharmacist</option>
                                <option value="admin">Admin</option>
                            </select>
                            <button
                                type="submit"
                                className="w-full bg-green-600 text-white p-3 rounded-md hover:bg-green-700 transition duration-300 ease-in-out font-semibold shadow-md flex items-center justify-center"
                            >
                                <UserPlus className="mr-2" size={20} /> Register
                            </button>
                        </form>
                    </div>
                ) : (
                    <div className="text-center">
                        <button
                            onClick={handleLogout}
                            className="bg-red-500 text-white p-3 rounded-md hover:bg-red-600 transition duration-300 ease-in-out font-semibold shadow-md flex items-center justify-center mx-auto"
                        >
                            <LogOut className="mr-2" size={20} /> Logout
                        </button>
                    </div>
                )}
            </div>

            {token && currentUser && (
                <>
                    {/* Add New Patient Form (Conditional based on role) */}
                    {hasRole(['admin', 'receptionist', 'nurse']) && (
                        <div className="bg-white p-8 rounded-xl shadow-xl w-full max-w-3xl mb-8 border border-blue-200">
                            <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center flex items-center justify-center">
                                <PlusCircle className="mr-3 text-blue-600" size={28} /> Add New Patient
                            </h2>
                            <form onSubmit={addPatient} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <input type="text" name="first_name" placeholder="First Name" value={newPatient.first_name} onChange={handleNewPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                <input type="text" name="last_name" placeholder="Last Name" value={newPatient.last_name} onChange={handleNewPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                <input type="email" name="email" placeholder="Email" value={newPatient.email} onChange={handleNewPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                <input type="tel" name="phone_number" placeholder="Phone Number" value={newPatient.phone_number} onChange={handleNewPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                <input type="date" name="date_of_birth" placeholder="Date of Birth" value={newPatient.date_of_birth} onChange={handleNewPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                <input type="text" name="address" placeholder="Address" value={newPatient.address} onChange={handleNewPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                <select name="gender" value={newPatient.gender} onChange={handleNewPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm">
                                    <option value="">Select Gender</option>
                                    <option value="Male">Male</option>
                                    <option value="Female">Female</option>
                                    <option value="Other">Other</option>
                                    <option value="Prefer not to say">Prefer not to say</option>
                                </select>
                                <button type="submit" className="col-span-1 md:col-span-2 bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 transition duration-300 ease-in-out font-semibold shadow-lg transform hover:-translate-y-1 flex items-center justify-center">
                                    <PlusCircle className="mr-2" size={20} /> Add Patient
                                </button>
                            </form>
                        </div>
                    )}

                    {/* Patient List (Conditional based on role) */}
                    {hasRole(['admin', 'doctor', 'receptionist', 'nurse']) && (
                        <div className="bg-white p-8 rounded-xl shadow-xl w-full max-w-5xl mb-8 border border-blue-200">
                            <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">Patient List</h2>
                            {patients.length === 0 ? (
                                <p className="text-gray-500 text-center py-4">No patients registered yet.</p>
                            ) : (
                                <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {patients.map((patient) => (
                                                <tr key={patient.id} className="hover:bg-gray-50 transition-colors duration-150">
                                                    <td className="py-3 px-4 text-sm text-gray-900">{patient.id}</td>
                                                    <td className="py-3 px-4 text-sm text-gray-900">{patient.first_name} {patient.last_name}</td>
                                                    <td className="py-3 px-4 text-sm text-gray-900">{patient.email}</td>
                                                    <td className="py-3 px-4 text-sm text-gray-900">{patient.phone_number}</td>
                                                    <td className="py-3 px-4 text-sm flex space-x-2">
                                                        {hasRole(['admin', 'receptionist', 'nurse']) && (
                                                            <button
                                                                onClick={() => startEditPatient(patient)}
                                                                className="p-2 bg-yellow-500 text-white rounded-full hover:bg-yellow-600 transition duration-200 shadow-md transform hover:scale-105"
                                                                title="Edit Patient"
                                                            >
                                                                <Edit size={16} />
                                                            </button>
                                                        )}
                                                        {hasRole('admin') && (
                                                            <button
                                                                onClick={() => deletePatient(patient.id)}
                                                                className="p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition duration-200 shadow-md transform hover:scale-105"
                                                                title="Delete Patient"
                                                            >
                                                                <Trash2 size={16} />
                                                            </button>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Edit Patient Modal/Form */}
                    {editingPatient && (
                        <div className="fixed inset-0 bg-gray-900 bg-opacity-70 flex items-center justify-center z-50 p-4 animate-fade-in">
                            <div className="bg-white p-10 rounded-xl shadow-2xl w-full max-w-xl border border-blue-300 transform scale-95 animate-scale-in">
                                <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">Edit Patient</h2>
                                <form onSubmit={updatePatient} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <input type="text" name="first_name" placeholder="First Name" value={editingPatient.first_name} onChange={handleEditPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                    <input type="text" name="last_name" placeholder="Last Name" value={editingPatient.last_name} onChange={handleEditPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                    <input type="email" name="email" placeholder="Email" value={editingPatient.email} onChange={handleEditPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                    <input type="tel" name="phone_number" placeholder="Phone Number" value={editingPatient.phone_number} onChange={handleEditPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                    <input type="date" name="date_of_birth" placeholder="Date of Birth" value={editingPatient.date_of_birth} onChange={handleEditPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                    <input type="text" name="address" placeholder="Address" value={editingPatient.address} onChange={handleEditPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm" />
                                    <select name="gender" value={editingPatient.gender} onChange={handleEditPatientChange} required className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 shadow-sm">
                                        <option value="">Select Gender</option>
                                        <option value="Male">Male</option>
                                        <option value="Female">Female</option>
                                        <option value="Other">Other</option>
                                        <option value="Prefer not to say">Prefer not to say</option>
                                    </select>
                                    <div className="col-span-1 md:col-span-2 flex justify-end space-x-4 mt-6">
                                        <button type="button" onClick={() => setEditingPatient(null)} className="bg-gray-300 text-gray-800 p-3 rounded-lg hover:bg-gray-400 transition duration-300 ease-in-out font-semibold shadow-md flex items-center">
                                            <XCircle className="mr-2" size={20} /> Cancel
                                        </button>
                                        <button type="submit" className="bg-green-600 text-white p-3 rounded-lg hover:bg-green-700 transition duration-300 ease-in-out font-semibold shadow-md flex items-center">
                                            <CheckCircle className="mr-2" size={20} /> Update Patient
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    )}

                    {/* AI Chatbot Section (Conditional based on role) */}
                    {hasRole(['admin', 'doctor']) && (
                        <div className="bg-white p-8 rounded-xl shadow-xl w-full max-w-3xl border border-blue-200">
                            <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center flex items-center justify-center">
                                <MessageSquare className="mr-3 text-purple-600" size={28} /> AI Chatbot
                            </h2>
                            <form onSubmit={sendChatbotQuery} className="flex flex-col gap-4">
                                <textarea
                                    rows="4"
                                    placeholder="Ask about patient info (e.g., 'What are the details for patient ID 1?', 'List all patients', 'Show appointments for patient ID 2')"
                                    value={chatbotQuery}
                                    onChange={(e) => setChatbotQuery(e.target.value)}
                                    className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition duration-200 shadow-sm resize-y"
                                    required
                                ></textarea>
                                <button type="submit" className="bg-purple-600 text-white p-3 rounded-lg hover:bg-purple-700 transition duration-300 ease-in-out font-semibold shadow-lg transform hover:-translate-y-1 flex items-center justify-center">
                                    <MessageSquare className="mr-2" size={20} /> Ask Chatbot
                                </button>
                            </form>
                            {chatbotResponse && (
                                <div className="mt-6 p-5 bg-gray-50 border border-gray-200 rounded-lg whitespace-pre-wrap text-gray-800 shadow-inner max-h-60 overflow-y-auto">
                                    <h3 className="font-semibold text-lg text-gray-700 mb-3">Chatbot Response:</h3>
                                    <p>{chatbotResponse}</p>
                                </div>
                            )}
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default App;
