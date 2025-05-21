document.addEventListener('DOMContentLoaded', function () {
    var modals = document.querySelectorAll('.modal');
    modals.forEach(function (modal) {
        new bootstrap.Modal(modal);
    });

    var forms = document.querySelectorAll('.modal form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            // Check form validity
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    modals.forEach(function (modal) {
        modal.addEventListener('hidden.bs.modal', function () {
            var forms = this.querySelectorAll('form');
            forms.forEach(function (form) {
                form.reset();
                form.classList.remove('was-validated');
            });
        });
    });

    var deleteButtons = document.querySelectorAll('[data-bs-target^="#delete"]');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            if (!confirm('Are you sure you want to delete this item?')) {
                event.preventDefault();
            }
        });
    });
}); 