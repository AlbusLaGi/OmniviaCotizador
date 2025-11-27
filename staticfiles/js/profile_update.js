document.addEventListener('DOMContentLoaded', function() {
    const paisSelect = document.getElementById('id_pais');
    const departamentoSelect = document.getElementById('id_departamento');
    const municipioSelect = document.getElementById('id_municipio');
    let colombiaLocationData = [];
    let allCountriesData = []; // Added for full country list

    // Store initial values
    const initialPais = paisSelect ? paisSelect.value : '';
    const initialDepartamento = departamentoSelect ? departamentoSelect.value : '';
    const initialMunicipio = municipioSelect ? municipioSelect.value : '';

    // Fetch all countries data
    fetch('/static/data/countries.json')
        .then(response => response.json())
        .then(data => {
            allCountriesData = data;
            populatePaises(() => {
                if (paisSelect && initialPais) {
                    paisSelect.value = initialPais;
                }
            });
        })
        .catch(error => console.error('Error fetching countries data:', error));

    // Fetch Colombia location data
    fetch('/static/data/colombia_location_data.json')
        .then(response => response.json())
        .then(data => {
            colombiaLocationData = data;
            // Populate departments and municipalities if initial country is Colombia
            if (initialPais === 'Colombia') {
                populateDepartamentos(() => {
                    if (departamentoSelect && initialDepartamento) {
                        departamentoSelect.value = initialDepartamento;
                    }
                    populateMunicipios(() => {
                        if (municipioSelect && initialMunicipio) {
                            municipioSelect.value = initialMunicipio;
                        }
                    });
                });
            }
        })
        .catch(error => console.error('Error fetching Colombia location data:', error));

    function populatePaises(callback) {
        if (!paisSelect) return; // Ensure paisSelect exists
        paisSelect.innerHTML = '<option value="">Selecciona un país</option>';
        allCountriesData.forEach(country => {
            const option = document.createElement('option');
            option.value = country.name;
            option.textContent = country.name;
            paisSelect.appendChild(option);
        });
        if (callback) callback();
    }

    function populateDepartamentos(callback) {
        if (!departamentoSelect || !municipioSelect) return;
        departamentoSelect.innerHTML = '<option value="">Selecciona un departamento</option>';
        municipioSelect.innerHTML = '<option value="">Selecciona un municipio</option>';

        const selectedPais = paisSelect ? paisSelect.value : '';
        if (selectedPais === 'Colombia') {
            colombiaLocationData.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept.departamento;
                option.textContent = dept.departamento;
                departamentoSelect.appendChild(option);
            });
        }
        if (callback) callback();
    }

    function populateMunicipios(callback) {
        if (!departamentoSelect || !municipioSelect) return;
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
        if (callback) callback();
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

    // Lógica para el modal de actualización de perfil
    const updateProfileModal = document.getElementById('updateProfileModal');
    if (updateProfileModal) {
        updateProfileModal.addEventListener('shown.bs.modal', function () {
            // Re-fetch form elements inside the modal to ensure they are available
            const modalPaisSelect = document.getElementById('id_pais');
            const modalDepartamentoSelect = document.getElementById('id_departamento');
            const modalMunicipioSelect = document.getElementById('id_municipio');

            // Re-populate dropdowns if needed, and set initial values
            if (modalPaisSelect) {
                // Assuming populatePaises is global or accessible
                populatePaises(() => {
                    modalPaisSelect.value = initialPais;
                    if (modalPaisSelect.value === 'Colombia') {
                        populateDepartamentos(() => {
                            modalDepartamentoSelect.value = initialDepartamento;
                            populateMunicipios(() => {
                                modalMunicipioSelect.value = initialMunicipio;
                            });
                        });
                    }
                });
            }

            // Lógica para tipoEntidadSelect y otroTipoEntidadWrapper dentro del modal
            const tipoEntidadSelect = document.getElementById('id_tipo_entidad');
            const otroTipoEntidadWrapper = document.getElementById('otroTipoEntidadWrapperReg'); // Assuming same ID for update modal
            const otroTipoEntidadField = document.getElementById('id_otro_tipo_entidad'); // Assuming same ID

            function toggleOtroTipoEntidadModal() {
                if (tipoEntidadSelect && otroTipoEntidadWrapper) {
                    if (tipoEntidadSelect.value === 'Otro') {
                        otroTipoEntidadWrapper.style.display = 'block';
                    } else {
                        otroTipoEntidadWrapper.style.display = 'none';
                        if (otroTipoEntidadField) {
                            otroTipoEntidadField.value = '';
                        }
                    }
                }
            }

            if (tipoEntidadSelect) {
                toggleOtroTipoEntidadModal();
                tipoEntidadSelect.addEventListener('change', toggleOtroTipoEntidadModal);
            }
        });

        const profileUpdateForm = document.getElementById('profileUpdateForm');
        if (profileUpdateForm) {
            profileUpdateForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(profileUpdateForm);
                const csrfToken = formData.get('csrfmiddlewaretoken');
                const errorDiv = document.getElementById('profile-update-error');
                
                errorDiv.style.display = 'none';
                errorDiv.textContent = '';
                document.querySelectorAll('#profileUpdateForm .invalid-feedback').forEach(el => el.textContent = '');
                document.querySelectorAll('#profileUpdateForm .is-invalid').forEach(el => el.classList.remove('is-invalid'));

                fetch(profileUpdateForm.action, {
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
                        alert(data.message);
                        window.location.reload(); // Recargar la página para mostrar los datos actualizados
                    }
                })
                .catch(error => {
                    console.error('Error al actualizar perfil:', error);
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
                        errorDiv.textContent = 'Ocurrió un error inesperado al actualizar el perfil. Por favor, intente de nuevo.';
                        errorDiv.style.display = 'block';
                    }
                });
            });
        }
    }

    // Lógica para el modal de eliminación de cuenta
    const deleteAccountModal = document.getElementById('deleteAccountModal');
    if (deleteAccountModal) {
        const confirmPasswordInput = document.getElementById('confirmPassword');
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        const passwordErrorDiv = document.getElementById('passwordError');

        // Clear password input and error message when modal is shown
        deleteAccountModal.addEventListener('shown.bs.modal', function () {
            if (confirmPasswordInput) {
                confirmPasswordInput.value = '';
            }
            if (passwordErrorDiv) {
                passwordErrorDiv.style.display = 'none';
                passwordErrorDiv.textContent = '';
            }
            if (confirmDeleteBtn) {
                confirmDeleteBtn.disabled = true;
            }
        });

        if (confirmPasswordInput && confirmDeleteBtn) {
            confirmPasswordInput.addEventListener('input', function() {
                // Simply enable the button if there's some input, actual verification happens on click
                if (this.value.length > 0) {
                    confirmDeleteBtn.disabled = false;
                } else {
                    confirmDeleteBtn.disabled = true;
                }
                passwordErrorDiv.style.display = 'none'; // Hide error on new input
            });

            confirmDeleteBtn.addEventListener('click', function() {
                if (confirmDeleteBtn.disabled) return;

                const password = confirmPasswordInput.value;
                if (!password) {
                    passwordErrorDiv.textContent = 'Por favor, ingresa tu contraseña.';
                    passwordErrorDiv.style.display = 'block';
                    return;
                }

                fetch("{% url 'delete_account' %}", {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json', // Specify content type for JSON body
                        'Accept': 'application/json',
                    },
                    body: JSON.stringify({ password: password }), // Send password in JSON body
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw err; });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        window.location.href = data.redirect_url;
                    } else {
                        passwordErrorDiv.textContent = data.message || 'Contraseña incorrecta o error al eliminar.';
                        passwordErrorDiv.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Error al eliminar la cuenta:', error);
                    passwordErrorDiv.textContent = 'Ocurrió un error inesperado al eliminar la cuenta. Por favor, intente de nuevo.';
                    passwordErrorDiv.style.display = 'block';
                });
            });
        }
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});