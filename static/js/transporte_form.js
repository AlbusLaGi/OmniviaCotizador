document.addEventListener('DOMContentLoaded', function() {
    // Buscar cualquier campo de entrada en el formulario de transporte para añadir autocompletado
    const searchInputs = document.querySelectorAll('input[name="nombre"], input[name="marca"], input[name="modelo"], input[name="matricula"]');
    const searchInput = searchInputs.length > 0 ? searchInputs[0] : null;
    
    if (searchInput) {
        // Crear contenedor de autocompletar si no existe
        let autocompleteContainer = document.getElementById('autocomplete-results-transporte');
        if (!autocompleteContainer) {
            autocompleteContainer = document.createElement('div');
            autocompleteContainer.id = 'autocomplete-results-transporte';
            autocompleteContainer.className = 'autocomplete-dropdown';
            autocompleteContainer.style.cssText = 'position: absolute; top: 100%; left: 0; width: 100%; max-height: 300px; overflow-y: auto; z-index: 1000; display: none; box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15); background: white; border: 1px solid rgba(0,0,0,0.15); border-radius: 0.375rem;';
            
            // Asegurarse que el contenedor padre tenga position: relative para que el contenedor de autocompletar funcione correctamente
            searchInput.parentNode.style.position = 'relative';
            searchInput.parentNode.appendChild(autocompleteContainer);
        }

        let currentIndex = -1;

        // Manejar eventos de teclado para navegación
        searchInput.addEventListener('keydown', function(e) {
            const items = autocompleteContainer.querySelectorAll('.autocomplete-item');
            if (!items.length || currentIndex === -1) return;

            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    currentIndex = (currentIndex < items.length - 1) ? currentIndex + 1 : 0;
                    updateActiveItem(Array.from(items));
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    currentIndex = (currentIndex > 0) ? currentIndex - 1 : items.length - 1;
                    updateActiveItem(Array.from(items));
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (currentIndex >= 0 && items[currentIndex]) {
                        items[currentIndex].click();
                    }
                    break;
                case 'Escape':
                    autocompleteContainer.style.display = 'none';
                    currentIndex = -1;
                    break;
            }
        });

        function updateActiveItem(items) {
            items.forEach((item, index) => {
                if (index === currentIndex) {
                    item.classList.add('active');
                    item.style.backgroundColor = '#0d6efd';
                    item.style.color = 'white';
                } else {
                    item.classList.remove('active');
                    item.style.backgroundColor = '';
                    item.style.color = '';
                }
            });
        }

        // Manejar el evento de entrada para mostrar autocompletar
        let timeout = null;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            const query = this.value.toLowerCase().trim();
            
            if (query.length === 0) {
                autocompleteContainer.style.display = 'none';
                currentIndex = -1;
                return;
            }

            // Realizar búsqueda con demora para evitar múltiples solicitudes rápidas
            timeout = setTimeout(() => {
                // Cargar sugerencias para mostrar autocompletar
                fetch('/api/autocomplete-transportes/?q=' + encodeURIComponent(query))
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            const filteredSuggestions = data.transportes;

                            if (filteredSuggestions.length > 0) {
                                autocompleteContainer.innerHTML = '';
                                currentIndex = -1;

                                filteredSuggestions.forEach((transporte, index) => {
                                    const item = document.createElement('div');
                                    item.className = 'autocomplete-item';
                                    item.style.cssText = 'padding: 0.5rem 1rem; cursor: pointer; border-bottom: 1px solid #eee;';

                                    // Resaltar la parte que coincide con la búsqueda
                                    const regex = new RegExp(`(${query})`, 'gi');
                                    let displayText = '';
                                    
                                    if (transporte.nombre && transporte.nombre.toLowerCase().includes(query)) {
                                        displayText = transporte.nombre.replace(regex, '<strong>$1</strong>');
                                    } else if (transporte.marca && transporte.marca.toLowerCase().includes(query)) {
                                        displayText = `${transporte.nombre || 'Sin nombre'} - <strong>${transporte.marca}</strong>`;
                                    } else if (transporte.modelo && transporte.modelo.toLowerCase().includes(query)) {
                                        displayText = `${transporte.nombre || 'Sin nombre'} - <strong>${transporte.modelo}</strong>`;
                                    } else if (transporte.matricula && transporte.matricula.toLowerCase().includes(query)) {
                                        displayText = `${transporte.nombre || 'Sin nombre'} - Placa: <strong>${transporte.matricula}</strong>`;
                                    } else {
                                        // Si no hay coincidencia exacta, mostrar información resumida con coincidencias destacadas
                                        displayText = `${transporte.nombre || 'Sin nombre'} ${transporte.marca ? `- ${transporte.marca}` : ''} ${transporte.matricula ? `(${transporte.matricula})` : ''}`;
                                        displayText = displayText.replace(new RegExp(`(${query})`, 'gi'), '<strong>$1</strong>');
                                    }
                                    
                                    item.innerHTML = displayText;

                                    item.addEventListener('click', function() {
                                        // Llenar los campos del formulario con los datos del transporte seleccionado
                                        autocompleteContainer.style.display = 'none';
                                        currentIndex = -1;

                                        if (transporte.nombre) {
                                            const nombreField = document.getElementById('id_nombre') || document.querySelector('input[name="nombre"]');
                                            if (nombreField) nombreField.value = transporte.nombre;
                                        }
                                        if (transporte.marca) {
                                            const marcaField = document.getElementById('id_marca') || document.querySelector('input[name="marca"]');
                                            if (marcaField) marcaField.value = transporte.marca;
                                        }
                                        if (transporte.modelo) {
                                            const modeloField = document.getElementById('id_modelo') || document.querySelector('input[name="modelo"]');
                                            if (modeloField) modeloField.value = transporte.modelo;
                                        }
                                        if (transporte.matricula) {
                                            const matriculaField = document.getElementById('id_matricula') || document.querySelector('input[name="matricula"]');
                                            if (matriculaField) matriculaField.value = transporte.matricula;
                                        }
                                        if (transporte.modeloTransporte) {
                                            const modeloTransporteField = document.getElementById('id_modeloTransporte') || document.querySelector('select[name="modeloTransporte"]');
                                            if (modeloTransporteField) modeloTransporteField.value = transporte.modeloTransporte;
                                        }
                                    });

                                    item.addEventListener('mouseenter', function() {
                                        currentIndex = index;
                                        updateActiveItem(Array.from(autocompleteContainer.querySelectorAll('.autocomplete-item')));
                                    });

                                    autocompleteContainer.appendChild(item);
                                });

                                autocompleteContainer.style.display = 'block';
                            } else {
                                autocompleteContainer.style.display = 'none';
                            }
                        } else {
                            autocompleteContainer.style.display = 'none';
                        }
                    })
                    .catch(error => {
                        console.error('Error al obtener sugerencias:', error);
                        autocompleteContainer.style.display = 'none';
                    });
            }, 300); // Demora de 300ms para evitar búsquedas constantes
        });

        searchInput.addEventListener('focus', function() {
            if (this.value.trim().length > 0) {
                autocompleteContainer.style.display = 'block';
            }
        });

        searchInput.addEventListener('blur', function() {
            setTimeout(() => {
                autocompleteContainer.style.display = 'none';
            }, 200);
        });
    }
});