// C:\Users\Faith\Downloads\myits-collab\frontend\public\js\main.js

const API_BASE_URL = 'http://127.0.0.1:8000'; // Your FastAPI backend URL

// --- Utility Functions (Reusable helpers) ---
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Accept': 'application/json'
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

function getJsonAuthHeaders() {
    const headers = getAuthHeaders();
    headers['Content-Type'] = 'application/json';
    return headers;
}

function displayMessage(type, message, targetElementId) {
    const targetElement = document.getElementById(targetElementId);
    if (!targetElement) return;

    targetElement.textContent = '';
    targetElement.style.color = (type === 'success') ? 'green' : 'red';
    targetElement.textContent = message;
}

function isLoggedIn() {
    return localStorage.getItem('access_token') !== null;
}

function getUserRole() {
    return localStorage.getItem('user_role');
}

function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    alert('Logged out!');
    window.location.href = 'login.html';
}

function updateNavLinks() {
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', handleLogout);
        logoutButton.style.display = isLoggedIn() ? 'inline-block' : 'none';
    }

    const createProjectLink = document.querySelector('a[href="project_create.html"]');
    if (createProjectLink) {
        const userRole = getUserRole();
        if (userRole === 'dosen' || userRole === 'admin') {
            createProjectLink.style.display = 'flex'; // Use flex for icon alignment
        } else {
            createProjectLink.style.display = 'none';
        }
    }

    const loggedInUserNameSpan = document.getElementById('loggedInUserName');
    if (loggedInUserNameSpan) {
        if (isLoggedIn()) {
            loggedInUserNameSpan.textContent = `Loading User...`; // Show loading while fetching
            // Fetch actual user name
            fetch(`${API_BASE_URL}/users/me`, {headers: getAuthHeaders()})
                .then(res => {
                    if (!res.ok) {
                        // If token is invalid/expired here, logout
                        if (res.status === 401 || res.status === 403) {
                            handleLogout(); // This will clear token and redirect
                        }
                        throw new Error(`HTTP error! status: ${res.status}`);
                    }
                    return res.json();
                })
                .then(data => {
                    // Display actual name based on the data received
                    // Assuming response data keys match Pydantic response schemas (e.g., Nama_Dosen, Nama_Mahasiswa)
                    const userName = data.Nama_Mahasiswa || data.Nama_Dosen || data.Nama_Admin || `(${getUserRole()})`;
                    loggedInUserNameSpan.textContent = userName;
                })
                .catch(err => {
                    console.error("Failed to fetch user profile:", err);
                    loggedInUserNameSpan.textContent = `(${getUserRole()})`; // Fallback to role if fetch fails
                });
        } else {
            loggedInUserNameSpan.textContent = 'Guest'; // If not logged in, show 'Guest'
        }
    }
}


// --- Login Page Logic ---
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const loginMessageElement = document.getElementById('loginMessage');
        loginMessageElement.textContent = '';

        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                },
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `Login failed! Status: ${response.status}`);
            }

            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user_role', data.user_role);
            alert('Login successful!');
            window.location.href = 'index.html';
        } catch (error) {
            console.error('Login error:', error);
            loginMessageElement.textContent = `Login failed: ${error.message}`;
        }
    });
}


// --- Dashboard Page Logic ---
async function fetchProjects() {
    const projectsContainer = document.getElementById('projects-container');
    if (!projectsContainer) return;

    if (!isLoggedIn()) {
        alert('Please log in first!');
        window.location.href = 'login.html';
        return;
    }

    projectsContainer.innerHTML = '<p>Loading projects...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/projects`, {
            method: 'GET',
            headers: getAuthHeaders(),
        });

        const projects = await response.json();

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                localStorage.removeItem('access_token'); localStorage.removeItem('user_role');
                alert('Session expired or unauthorized. Please log in again.'); window.location.href = 'login.html'; return;
            }
            throw new Error(projects.detail || `HTTP error! status: ${response.status}`);
        }

        console.log('Fetched projects:', projects);

        if (projects.length === 0) {
            projectsContainer.innerHTML = '<p>No projects available yet.</p>';
            return;
        }

        projectsContainer.innerHTML = '';

        projects.forEach(project => {
            const projectCard = document.createElement('div');
            projectCard.className = 'project-card';
            // Determine status badge class and text
            const statusClass = project.Availability ? 'open' : 'closed';
            const statusText = project.Availability ? 'Open' : 'Closed';

            projectCard.innerHTML = `
                <div class="status-badge ${statusClass}">${statusText}</div>
                <h3>${project.Judul}</h3>
                <p>${project.Deskripsi ? project.Deskripsi.substring(0, 100) + '...' : 'No description'}</p>
                <p><strong>Bidang:</strong> ${project.Bidang}</p> <p><strong>Uploader NIP:</strong> ${project.Dosen_NIP || project.Admin_ID_Admin || 'N/A'}</p> <button onclick="viewProjectDetails('${project.ID_Proyek}')">Details</button>
            `;
            projectsContainer.appendChild(projectCard);
        });

    } catch (error) {
        console.error('Error fetching projects:', error);
        projectsContainer.innerHTML = `<p>Error loading projects: ${error.message}. Please check console for details.</p>`;
    }
}

function viewProjectDetails(projectId) {
    window.location.href = `project_detail.html?id=${projectId}`;
}


// --- Project Creation Page Logic ---
async function handleCreateProject(event) {
    event.preventDefault();

    const form = event.target;
    const projectData = {
        Judul: form.Judul.value,
        Deskripsi: form.Deskripsi.value,
        Availability: form.Availability.checked,
        Bidang: form.Bidang.value
    };

    displayMessage('success', '', 'message');
    displayMessage('error', '', 'error');

    if (!isLoggedIn() || (getUserRole() !== 'dosen' && getUserRole() !== 'admin')) {
        displayMessage('error', 'You must be logged in as Dosen or Admin to create projects.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/projects/`, {
            method: 'POST',
            headers: getJsonAuthHeaders(),
            body: JSON.stringify(projectData)
        });

        const responseData = await response.json();

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                localStorage.removeItem('access_token'); localStorage.removeItem('user_role');
                alert('Session expired or unauthorized. Please log in again.'); window.location.href = 'login.html'; return;
            }
            throw new Error(responseData.detail || 'Failed to create project');
        }

        console.log('Project created successfully:', responseData);
        displayMessage('success', 'Project created successfully!', 'message');
        form.reset();

    } catch (error) {
        console.error('Error creating project:', error);
        displayMessage('error', `Error creating project: ${error.message}`, 'error');
    }
}


// --- Global DOMContentLoaded Listener ---
document.addEventListener('DOMContentLoaded', () => {
    updateNavLinks(); // Update nav links visibility for all pages

    if (document.getElementById('projects-container')) {
        fetchProjects(); // This is the dashboard page
    } else if (document.getElementById('createProjectForm')) {
        document.getElementById('createProjectForm').addEventListener('submit', handleCreateProject);
    }
});