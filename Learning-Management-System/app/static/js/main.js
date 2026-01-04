// Automatically close flash messages after 4 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 4000);
    });
});

// Smooth scroll for nav links (optional)
console.log("LearnHub JS Loaded Successfully!");