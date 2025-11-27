document.addEventListener('DOMContentLoaded', function() {
    const registrationModal = document.getElementById('registrationModal');
    const paisSelect = document.getElementById('id_pais');
    const departamentoSelect = document.getElementById('id_departamento');
    const municipioSelect = document.getElementById('id_municipio');
    let colombiaLocationData = [];
    let allCountriesData = [];

    // Fetch subcategories for datalist
    if (registrationModal) {
        registrationModal.addEventListener('show.bs.modal', function () {
            fetch('/api/subcategorias/')
                .then(response => response.json())
                .then(data => {
                    const datalist = document.getElementById('subcategoria-list');
                    datalist.innerHTML = ''; // Clear existing options
                    data.forEach(item => {
                        const option = document.createElement('option');
                        option.value = item;
                        datalist.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching subcategories:', error));

            // Fetch Colombia location data
            fetch('/static/data/colombia_location_data.json')
                .then(response => response.json())
                .then(data => {
                    colombiaLocationData = data;
                })
                .catch(error => console.error('Error fetching Colombia location data:', error));

            // Fetch all countries data
            fetch('/static/data/countries.json')
                .then(response => response.json())
                .then(data => {
                    allCountriesData = data;
                    populatePaises();
                })
                .catch(error => console.error('Error fetching countries data:', error));
        });

        registrationModal.addEventListener('shown.bs.modal', function () {
            // Lógica para tipoEntidadSelect y otroTipoEntidadWrapper
            const tipoEntidadSelect = document.getElementById('id_tipo_entidad');
            const otroTipoEntidadWrapper = document.getElementById('otroTipoEntidadWrapperReg');
            const otroTipoEntidadField = document.getElementById('id_otro_tipo_entidad');

            function toggleOtroTipoEntidad() {
                if (tipoEntidadSelect && otroTipoEntidadWrapper) { // Add null checks
                    if (tipoEntidadSelect.value === 'Otro') {
                        otroTipoEntidadWrapper.style.display = 'block';
                    } else {
                        otroTipoEntidadWrapper.style.display = 'none';
                        if (otroTipoEntidadField) {
                            otroTipoEntidadField.value = ''; // Clear the value when hidden
                        }
                    }
                }
            }

            if (tipoEntidadSelect) {
                toggleOtroTipoEntidad();
                tipoEntidadSelect.addEventListener('change', toggleOtroTipoEntidad);
            }
        });
    }

    function populatePaises() {
        if (!paisSelect) return; // Ensure paisSelect exists
        paisSelect.innerHTML = '<option value="">Selecciona un país</option>';
        allCountriesData.forEach(country => {
            const option = document.createElement('option');
            option.value = country.name;
            option.textContent = country.name;
            paisSelect.appendChild(option);
        });
    }

    function populateDepartamentos() {
        if (!departamentoSelect || !municipioSelect) return; // Ensure elements exist
        departamentoSelect.innerHTML = '<option value="">Selecciona un departamento</option>';
        municipioSelect.innerHTML = '<option value="">Selecciona un municipio</option>';

        colombiaLocationData.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept.departamento;
            option.textContent = dept.departamento;
            departamentoSelect.appendChild(option);
        });
    }

    function populateMunicipios() {
        if (!departamentoSelect || !municipioSelect) return; // Ensure elements exist
        const selectedDepartamento = departamentoSelect.value;
        municipioSelect.innerHTML = '<option value="">Selecciona un municipio</option>';

        if (selectedDepartamento) {
            const departamento = colombiaLocationData.find(dept => dept.departamento === selectedDepartamento);
            if (departamento) {
                departamento.ciudades.forEach(ciudad => {
                    const option = document.createElement('option');
                    option.value = ciudad;
                    option.textContent = ciudad;
                    municipioSelect.appendChild(option);
                });
            }
        }
    }

    if(paisSelect) {
        paisSelect.addEventListener('change', function() {
            if (this.value === 'Colombia') {
                populateDepartamentos();
            } else {
                departamentoSelect.innerHTML = '<option value="">Selecciona un departamento</option>';
                municipioSelect.innerHTML = '<option value="">Selecciona un municipio</option>';
            }
        });
    }

    if(departamentoSelect){
        departamentoSelect.addEventListener('change', populateMunicipios);
    }

    const registrationForm = document.getElementById('registrationForm');
    if (!registrationForm) {
        return;
    }

    const usernameInput = document.getElementById('id_username');
    const usernameFeedback = document.getElementById('username-feedback-reg');
    const alphanumericRegex = /^[a-zA-Z0-9]*$/;

    if (usernameInput && usernameFeedback) {
        // Check for invalid characters as user types
        usernameInput.addEventListener('input', function() {
            const username = this.value;
            if (!alphanumericRegex.test(username)) {
                usernameFeedback.textContent = 'Solo se permiten caracteres alfanuméricos sin espacios.';
                usernameFeedback.className = 'form-text text-danger';
            } else {
                // Clear the message if valid, so the availability check can show its message
                if (usernameFeedback.textContent.includes('alfanuméricos')) {
                    usernameFeedback.textContent = '';
                    usernameFeedback.className = 'form-text';
                }
            }
        });

        // Check for availability on blur
        usernameInput.addEventListener('blur', function() {
            const username = this.value;

            // First, ensure the format is valid before checking availability
            if (!alphanumericRegex.test(username)) {
                usernameFeedback.textContent = 'Solo se permiten caracteres alfanuméricos sin espacios.';
                usernameFeedback.className = 'form-text text-danger';
                return; // Stop if format is invalid
            }

            if (username.length > 0) {
                fetch(`/api/check_username/?username=${username}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.is_taken) {
                            usernameFeedback.textContent = 'Este nombre de usuario ya está en uso.';
                            usernameFeedback.className = 'form-text text-danger';
                        } else {
                            usernameFeedback.textContent = 'Nombre de usuario disponible.';
                            usernameFeedback.className = 'form-text text-success';
                        }
                    })
                    .catch(error => {
                        console.error('Error checking username availability:', error);
                        usernameFeedback.textContent = 'Error al verificar disponibilidad.';
                        usernameFeedback.className = 'form-text text-warning';
                    });
            } else {
                usernameFeedback.textContent = '';
            }
        });
    }

    const passwordInput = document.getElementById('id_password');
    const password2Input = document.getElementById('id_password2');
    const passwordMatchFeedback = document.getElementById('password-match-feedback-reg');

    function checkPasswordMatch() {
        if (passwordInput.value.length > 0 && password2Input.value.length > 0) {
            if (passwordInput.value === password2Input.value) {
                passwordMatchFeedback.innerHTML = '<span style="color: green;">✓</span>';
            } else {
                passwordMatchFeedback.innerHTML = '<span style="color: red;">✗</span>';
            }
        } else {
            passwordMatchFeedback.innerHTML = '';
        }
    }

    if (passwordInput && password2Input && passwordMatchFeedback) {
        passwordInput.addEventListener('keyup', checkPasswordMatch);
        password2Input.addEventListener('keyup', checkPasswordMatch);
    }

    registrationForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(registrationForm);
        const csrfToken = formData.get('csrfmiddlewaretoken');
        const errorDiv = document.getElementById('registration-error');
        
        // Clear previous errors
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
        document.querySelectorAll('#registrationForm .invalid-feedback').forEach(el => el.textContent = '');
        document.querySelectorAll('#registrationForm .is-invalid').forEach(el => el.classList.remove('is-invalid'));

        fetch(registrationForm.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
            },
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const registrationSuccessModalElement = document.getElementById('registrationSuccessModal');
                const registrationSuccessMessageElement = document.getElementById('registrationSuccessMessage');
                if (registrationSuccessModalElement && registrationSuccessMessageElement) {
                    registrationSuccessMessageElement.textContent = data.message;
                    const registrationSuccessModal = new bootstrap.Modal(registrationSuccessModalElement);
                    registrationSuccessModal.show();

                    registrationSuccessModalElement.addEventListener('hidden.bs.modal', function () {
                        window.location.href = data.redirect_url;
                    }, { once: true }); // Ensure the event listener is removed after first use
                } else {
                    // Fallback if modal elements are not found
                    alert(data.message);
                    window.location.href = data.redirect_url;
                }
            }
        })
        .catch(error => {
            console.error('Form submission error:', error);
            if (error.errors) {
                for (const fieldName in error.errors) {
                    const fieldElement = document.getElementById(`id_${fieldName}`);
                    if (fieldElement) {
                        fieldElement.classList.add('is-invalid');
                        const errorFeedback = fieldElement.nextElementSibling;
                        if (errorFeedback && errorFeedback.classList.contains('invalid-feedback')) {
                            errorFeedback.textContent = error.errors[fieldName].join(' ');
                        }
                    }
                }
                if (error.errors.__all__) {
                    errorDiv.textContent = error.errors.__all__.join(' ');
                    errorDiv.style.display = 'block';
                }
            } else {
                errorDiv.textContent = 'Ocurrió un error inesperado. Por favor, intente de nuevo.';
                errorDiv.style.display = 'block';
            }
        });
    });
});