document.addEventListener('DOMContentLoaded', function () {
    console.log(typeof bootstrap);  // Check if Bootstrap is loaded

    // Initialize Bootstrap Modal (if not automatically initialized)
    var sidebarModal = document.getElementById('sidebarModal');
    if (sidebarModal) {
        var myModal = new bootstrap.Modal(sidebarModal, {
            keyboard: true
        });
    }

    // Event listeners for collapsible sections
    var collapsibles = document.querySelectorAll('[data-bs-toggle="collapse"]');
    collapsibles.forEach(function (collapsible) {
        collapsible.addEventListener('click', function () {
            var target = this.getAttribute('data-bs-target');
            var collapseElement = document.querySelector(target);
            if (collapseElement) {
                collapseElement.classList.toggle('show');
            }
        });
    });
});