
function toggleMenu(menuId) {
    const menu = document.getElementById(menuId);
    if (menu.style.display === 'block') {
        menu.style.display = 'none';
    } else {
        menu.style.display = 'block';
    }
}

function showForm(formId) {
    const forms = document.querySelectorAll('.form-container');
    forms.forEach(form => form.classList.remove('active'));
    const selectedForm = document.getElementById(formId);
    if (selectedForm) {
        selectedForm.classList.add('active');
    }
}

function uploadData(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch('/upload-data', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showPopup(data.message);
            } else if (data.error) {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error uploading data:', error);
            alert('An error occurred while uploading the data.');
        });
}

    
const downloadButton = document.getElementById('downloadButton');
const popup = document.getElementById('popup');
const popupMessage = document.getElementById('popupMessage');
const closePopup = document.getElementById('closePopup');

downloadButton.addEventListener('click', (event) => {
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;

    if (!startDate || !endDate) {
        alert('Please select both start and end dates.');
        // Prevent the form from submitting if dates are missing
        event.preventDefault();
        return;
    }

    // Show the popup with "Downloading..." message
    popupMessage.innerText = 'Downloading... Please wait.';
    popup.style.display = 'block';

    // Allow the form to proceed with its default behavior (POST to /download-data)
});

// Close the popup when the Close button is clicked
closePopup.addEventListener('click', () => {
    popup.style.display = 'none';
});


// --------------

// Function to toggle submenu visibility
function toggleMenu(menuId) {
    const menu = document.getElementById(menuId);
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

// Function to show a specific form and hide others
function showForm(formId) {
    const forms = document.querySelectorAll(".form-container");
    forms.forEach((form) => {
        form.style.display = "none"; // Hide all forms
    });

    const selectedForm = document.getElementById(formId);
    if (selectedForm) {
        selectedForm.style.display = "block"; // Show the selected form
    }
}

// Optional: Handle Report Form submission via JavaScript to show results dynamically
document.getElementById("reportForm")?.addEventListener("submit", async function (e) {
    e.preventDefault(); // Prevent default form submission
    const formData = new FormData(e.target);

    try {
        const response = await fetch(e.target.action, {
            method: "POST",
            body: formData,
        });

        const result = document.getElementById("result");
        if (response.ok) {
            const data = await response.json();
            result.textContent = JSON.stringify(data, null, 2);
        } else {
            const error = await response.json();
            result.textContent = `Error: ${error.error}`;
        }
    } catch (error) {
        console.error("Error submitting form:", error);
    }
});

