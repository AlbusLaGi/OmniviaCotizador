document.addEventListener('DOMContentLoaded', function() {
    // Funcionalidad de login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(loginForm);
            const data = Object.fromEntries(formData.entries());
            const csrfToken = data.csrfmiddlewaretoken;
            console.log("CSRF Token:", csrfToken); // For debugging

            const errorDiv = document.getElementById('login-error');
            errorDiv.style.display = 'none'; // Hide previous errors

            fetch('/api/ajax/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    username: data.username,
                    password: data.password,
                }),
            })
            .then(response => {
                if (!response.ok) {
                    // If response is not ok, get the error message from the body
                    return response.json().then(err => {
                        throw new Error(err.error || `Error ${response.status}: ${response.statusText}`);
                    });
                }
                return response.json();
            })
            .then(result => {
                if (result.success && result.redirect_url) {
                    window.location.href = result.redirect_url;
                } else {
                    // This part might not be reached if the server sends a non-2xx status
                    errorDiv.textContent = result.error || 'Ocurrió un error.';
                    errorDiv.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                errorDiv.textContent = error.message || 'Error de red o del servidor.';
                errorDiv.style.display = 'block';
            });
        });
    }

    // Funcionalidad de destino
    const destinoSelect = document.getElementById('destino-select');
    const destinoCardContainer = document.getElementById('destino-card-container');
    const destinosDataScript = document.getElementById('destinos-data');

    if (destinoSelect && destinoCardContainer && destinosDataScript) {
        const destinos = JSON.parse(destinosDataScript.textContent);

        destinoSelect.addEventListener('change', function() {
            const selectedDestinoId = this.value;
            destinoCardContainer.innerHTML = ''; // Clear previous content

            if (selectedDestinoId) {
                const selectedDestino = destinos.find(d => d.id == selectedDestinoId);

                if (selectedDestino) {
                    const cardHtml = `
                        <div class="card mt-3 shadow-sm">
                            <div class="card-body">
                                <h5 class="card-title">${selectedDestino.nombre}</h5>
                                <h6 class="card-subtitle mb-2 text-muted">${selectedDestino.ubicacion}</h6>
                                <p class="card-text">${selectedDestino.descripcion}</p>
                                <p class="card-text"><strong>Categoría:</strong> ${selectedDestino.categoria}</p>
                                <h6 class="mt-3">Actividades:</h6>
                                <ul class="list-group list-group-flush">
                                    ${selectedDestino.actividades.map(act => `
                                        <li class="list-group-item">
                                            ${act.atractivo_nombre} (${act.tipo_costo})
                                            ${act.precios && act.precios.length > 0 ? `
                                                <ul class="list-unstyled ms-3">
                                                    ${act.precios.map(precio => `
                                                        <li>${precio.categoria}: TA: ${precio.temporada_alta}, TM: ${precio.temporada_media}, TB: ${precio.temporada_baja}</li>
                                                    `).join('')}
                                                </ul>
                                            ` : ''}
                                        </li>
                                    `).join('')}
                                </ul>
                                <div class="mt-3">
                                    <a href="${selectedDestino.update_url}" class="btn btn-warning btn-sm me-2">Editar</a>
                                    <a href="${selectedDestino.delete_url}" class="btn btn-danger btn-sm">Eliminar</a>
                                </div>
                            </div>
                        </div>
                    `;
                    destinoCardContainer.innerHTML = cardHtml;
                }
            }
        });
    }
});