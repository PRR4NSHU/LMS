// Functionality to handle alerts auto-closing
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000); // Closes flash messages after 5 seconds
});

// Log message to confirm auth.js is loaded
console.log("Auth JS Loaded Successfully!");