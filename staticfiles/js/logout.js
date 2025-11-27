document.addEventListener('DOMContentLoaded', function() {
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default button action

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/api/ajax/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({}) // Send an empty JSON object
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mostrar el modal de éxito de logout
                    const logoutSuccessModal = new bootstrap.Modal(document.getElementById('logoutSuccessModal'));
                    logoutSuccessModal.show();

                    // Redirigir a la página de inicio después de un breve retraso
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1500); // Redirigir después de 1.5 segundos
                } else {
                    alert('Error al cerrar sesión: ' + data.message);
                }
                } else {
                    alert('Error al cerrar sesión: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ocurrió un error al intentar cerrar sesión.');
            });
        });
    }
});
