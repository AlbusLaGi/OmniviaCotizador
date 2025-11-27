document.addEventListener('DOMContentLoaded', function() {
    const originInput = document.getElementById('originInput');
    const destinationSelect = document.getElementById('destinationSelect');
    const adultsInput = document.getElementById('adultsInput');
    const childrenInput = document.getElementById('childrenInput');
    const fechaInicioInput = document.getElementById('fechaInicio');
    const fechaFinInput = document.getElementById('fechaFin');
    const hospedajeOptions = document.getElementById('hospedajeOptions');
    const hospedajeList = document.getElementById('hospedajeList');
    const otherServicesOptions = document.getElementById('otherServicesOptions');
    const alimentacionList = document.getElementById('alimentacionList');
    const transportList = document.getElementById('transportList');
    const seguroList = document.getElementById('seguroList');
    const calculateQuoteButton = document.getElementById('calculateQuoteButton');
    const quoteResult = document.getElementById('quoteResult');
    const resultDestination = document.getElementById('resultDestination');
    const resultPax = document.getElementById('resultPax');
    const resultHospedaje = document.getElementById('resultHospedaje');
    const resultServices = document.getElementById('resultServices');
    const totalPrice = document.getElementById('totalPrice');

    let allDestinos = [];
    let allHospedajes = [];
    let allAlimentacion = [];
    let allTransporte = [];
    let allSeguro = [];

    // Función para aplicar la animación fade-in
    function applyFadeIn(element) {
        element.classList.remove('fade-in'); // Reset animation
        void element.offsetWidth; // Trigger reflow
        element.classList.add('fade-in');
    }

    // Función para cargar destinos y servicios con filtros de fecha
    function fetchDataAndPopulateOptions() {
        const startDate = fechaInicioInput.value;
        const endDate = fechaFinInput.value;

        let queryParams = '';
        if (startDate) {
            queryParams += `?start_date=${startDate}`;
        }
        if (endDate) {
            queryParams += `${startDate ? '&' : '?'}end_date=${endDate}`;
        }

        // Limpiar opciones existentes
        destinationSelect.innerHTML = '<option value="" selected disabled>Seleccione un Destino</option>';
        hospedajeList.innerHTML = '';
        alimentacionList.innerHTML = '<h4>Alimentación</h4>';
        transportList.innerHTML = '<h4>Transporte</h4>';
        seguroList.innerHTML = '<h4>Seguro</h4>';

        hospedajeOptions.classList.add('d-none');
        otherServicesOptions.classList.add('d-none');
        calculateQuoteButton.classList.add('d-none');
        quoteResult.classList.add('d-none');

        // Cargar destinos
        fetch(`/api/destinos/${queryParams}`)
            .then(response => response.json())
            .then(data => {
                allDestinos = data;
                data.forEach(destino => {
                    const option = document.createElement('option');
                    option.value = destino.id;
                    option.textContent = destino.nombre;
                    destinationSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error cargando destinos:', error));

        // Cargar todos los hospedajes, alimentación, transporte y seguros
        Promise.all([
            fetch(`/api/hospedajes/${queryParams}`).then(res => res.json()),
            fetch(`/api/alimentacion/${queryParams}`).then(res => res.json()),
            fetch(`/api/transportes/${queryParams}`).then(res => res.json()),
            fetch(`/api/seguros/${queryParams}`).then(res => res.json())
        ]).then(data => {
            allHospedajes = data[0];
            allAlimentacion = data[1];
            allTransporte = data[2];
            allSeguro = data[3];
        }).catch(error => console.error('Error cargando servicios:', error));
    }

    // Cargar datos al iniciar y cuando cambian las fechas
    fetchDataAndPopulateOptions();
    fechaInicioInput.addEventListener('change', fetchDataAndPopulateOptions);
    fechaFinInput.addEventListener('change', fetchDataAndPopulateOptions);

    destinationSelect.addEventListener('change', function() {
        const selectedDestinationId = this.value;
        const selectedDestination = allDestinos.find(d => d.id == selectedDestinationId);

        hospedajeList.innerHTML = '';
        alimentacionList.innerHTML = '<h4>Alimentación</h4>';
        transportList.innerHTML = '<h4>Transporte</h4>';
        seguroList.innerHTML = '<h4>Seguro</h4>';

        hospedajeOptions.classList.add('d-none');
        otherServicesOptions.classList.add('d-none');
        calculateQuoteButton.classList.add('d-none');
        quoteResult.classList.add('d-none');

        if (selectedDestination) {
            // Mostrar hospedajes relacionados con el destino
            const relatedHospedajes = allHospedajes.filter(h => 
                h.ubicacion && selectedDestination.nombre && 
                h.ubicacion.toLowerCase().includes(selectedDestination.nombre.toLowerCase())
            );

            if (relatedHospedajes.length > 0) {
                hospedajeOptions.classList.remove('d-none');
                applyFadeIn(hospedajeOptions);
                relatedHospedajes.forEach(hospedaje => {
                    const card = `
                        <div class="col-md-4 mb-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">${hospedaje.nombreLugar}</h5>
                                    <p class="card-text">Tipo: ${hospedaje.tipoHospedaje}</p>
                                    <p class="card-text">Precio por noche: ${hospedaje.precio}</p>
                                    <p class="card-text">Restaurante: ${hospedaje.restaurante ? 'Sí' : 'No'}</p>
                                    <p class="card-text">Piscina: ${hospedaje.piscina ? 'Sí' : 'No'}</p>
                                    <div class="form-check">
                                        <input class="form-check-input hospedaje-checkbox" type="radio" name="selectedHospedaje" id="hospedaje-${hospedaje.id}" value="${hospedaje.id}" data-price="${hospedaje.precio}" data-name="${hospedaje.nombreLugar}">
                                        <label class="form-check-label" for="hospedaje-${hospedaje.id}">Seleccionar</label>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    hospedajeList.innerHTML += card;
                });
            }

            // Mostrar otros servicios
            otherServicesOptions.classList.remove('d-none');
            applyFadeIn(otherServicesOptions);
            calculateQuoteButton.classList.remove('d-none');
            applyFadeIn(calculateQuoteButton);


            // Alimentación
            allAlimentacion.forEach(item => {
                const checkbox = `
                    <div class="form-check">
                        <input class="form-check-input service-checkbox" type="checkbox" id="alimentacion-${item.id}" value="${item.id}" data-price="${item.precio}" data-name="${item.nombre}" data-type="Alimentacion">
                        <label class="form-check-label" for="alimentacion-${item.id}">${item.nombre} (${item.precio})</label>
                    </div>
                `;
                alimentacionList.innerHTML += checkbox;
            });

            // Transporte
            allTransporte.forEach(item => {
                const checkbox = `
                    <div class="form-check">
                        <input class="form-check-input service-checkbox" type="checkbox" id="transporte-${item.id}" value="${item.id}" data-price="${item.precio}" data-name="${item.nombre}" data-type="Transporte">
                        <label class="form-check-label" for="transporte-${item.id}">${item.tipoTransporte} - ${item.nombre} (${item.precio})</label>
                    </div>
                `;
                transportList.innerHTML += checkbox;
            });

            // Seguro
            allSeguro.forEach(item => {
                const checkbox = `
                    <div class="form-check">
                        <input class="form-check-input service-checkbox" type="checkbox" id="seguro-${item.id}" value="${item.id}" data-price="${item.precio}" data-name="${item.nombre}" data-type="Seguro">
                        <label class="form-check-label" for="seguro-${item.id}">${item.nombre} (${item.precio})</label>
                    </div>
                `;
                seguroList.innerHTML += checkbox;
            });
        }
    });

    calculateQuoteButton.addEventListener('click', function() {
        const selectedDestinationId = destinationSelect.value;
        const adults = parseInt(adultsInput.value);
        const children = parseInt(childrenInput.value);
        const totalPax = adults + children; // Total de personas
        let total = 0;
        let selectedServices = [];

        if (!selectedDestinationId) {
            alert('Por favor, seleccione un destino.');
            return;
        }

        const selectedHospedajeRadio = document.querySelector('input[name="selectedHospedaje"]:checked');
        let hospedajeName = 'Ninguno';
        if (selectedHospedajeRadio) {
            const hospedajePrice = parseFloat(selectedHospedajeRadio.dataset.price);
            hospedajeName = selectedHospedajeRadio.dataset.name;
            total += hospedajePrice * totalPax; // Asumiendo precio por persona por noche, o ajustar según modelo
            selectedServices.push(`Hospedaje: ${hospedajeName} (${hospedajePrice} x ${totalPax} pax)`);
        }

        document.querySelectorAll('.service-checkbox:checked').forEach(checkbox => {
            const servicePrice = parseFloat(checkbox.dataset.price);
            const serviceName = checkbox.dataset.name;
            const serviceType = checkbox.dataset.type;
            total += servicePrice * totalPax; // Asumiendo precio por persona
            selectedServices.push(`${serviceType}: ${serviceName} (${servicePrice} x ${totalPax} pax)`);
        });

        resultDestination.textContent = allDestinos.find(d => d.id == selectedDestinationId).nombre;
        resultPax.textContent = `Adultos: ${adults}, Niños: ${children}, Total: ${totalPax}`;
        resultHospedaje.textContent = hospedajeName;
        resultServices.innerHTML = '';
        selectedServices.forEach(service => {
            const li = document.createElement('li');
            li.textContent = service;
            resultServices.appendChild(li);
        });
        totalPrice.textContent = total.toFixed(2);
        quoteResult.classList.remove('d-none');
        applyFadeIn(quoteResult);
    });
});