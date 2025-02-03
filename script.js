const API_URL = "http://127.0.0.1:8000/api/v1/users"; // Adjust based on your backend

// Register User
document.getElementById("registerForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const fullName = document.getElementById("fullName").value;  
    const location = document.getElementById("location").value; 


    const response = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            username: username,
            password: password,
            user_email: email, 
            user_full_name: fullName,  
            user_location: location  
        })
    });

    const data = await response.json();
    console.log(response);
    alert(data.message || "User registered successfully!");
});

// Fetch Users
async function fetchUsers() {
    const response = await fetch(`${API_URL}/`);
    const users = await response.json();
    
    const tableBody = document.getElementById("userTableBody");
    users.forEach(user => {
        const row = `<tr>
                        <td>${user.username}</td>
                        <td>${user.user_email}</td>
                        <td>${user.user_full_name}</td>
                        <td>${user.user_location}</td>
                    </tr>`;
        tableBody.innerHTML += row;
    });
}

// Fetch Purchases
async function fetchPurchases() {
    const response = await fetch(`${API_URL}/purchases/total`);
    const data = await response.json();
    
    const list = document.getElementById("purchasesList");
    data.purchases.forEach(purchase => {
        list.innerHTML += `<li class="list-group-item">${purchase.product_title} - $${purchase.product_price}</li>`;
    });
}

// Load Users & Purchases on Page Load
window.onload = function () {
    if (document.getElementById("userTableBody")) fetchUsers();
    if (document.getElementById("purchasesList")) fetchPurchases();
};
