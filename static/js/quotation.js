document.addEventListener('DOMContentLoaded', function() {
    // Elementos del formulario
    const quotationForm = document.getElementById('quotationForm');
    const origenInput = document.getElementById('origen');
    const destinoSelect = document.getElementById('destino');
    const fechaInicioInput = document.getElementById('fecha_inicio');
    const fechaFinInput = document.getElementById('fecha_fin');
    const adultosInput = document.getElementById('adultos');
    const niniosInput = document.getElementById('ninios');
    const bebesInput = document.getElementById('bebes');
    const adultosMayoresInput = document.getElementById('adultos_mayores');
    const estudiantesInput = document.getElementById('estudiantes');
    const porcentajeUtilidadInput = document.getElementById('porcentaje_utilidad');

    // Elementos de resultado
    const quoteResult = document.getElementById('quoteResult');
    const resultOrigen = document.getElementById('resultOrigen');
    const resultDestination = document.getElementById('resultDestination');
    const resultFechaInicio = document.getElementById('resultFechaInicio');
    const resultFechaFin = document.getElementById('resultFechaFin');
    const resultTotalPax = document.getElementById('resultTotalPax');
    const resultPaxDetails = document.getElementById('resultPaxDetails');
    const resultUtilidad = document.getElementById('resultUtilidad');

    // Elementos de precios por pax
    const priceHospedajePax = document.getElementById('priceHospedajePax');
    const priceTransportePax = document.getElementById('priceTransportePax');
    const priceAlimentacionPax = document.getElementById('priceAlimentacionPax');
    const priceSeguroPax = document.getElementById('priceSeguroPax');

    // Elementos de totales
    const totalHospedaje = document.getElementById('totalHospedaje');
    const totalTransporte = document.getElementById('totalTransporte');
    const totalAlimentacion = document.getElementById('totalAlimentacion');
    const totalSeguro = document.getElementById('totalSeguro');

    // Elementos de impuestos y utilidad
    const ivaHospedaje = document.getElementById('ivaHospedaje');
    const ivaOtros = document.getElementById('ivaOtros');
    const subtotalConIva = document.getElementById('subtotalConIva');
    const utilidadPorcentaje = document.getElementById('utilidadPorcentaje');
    const montoUtilidad = document.getElementById('montoUtilidad');

    // Elementos de total final
    const totalFinal = document.getElementById('totalFinal');
    const precioPorPax = document.getElementById('precioPorPax');

    let allDestinos = [];

    // Función para cargar destinos
    function loadDestinations() {
        // Primero verificar si ya hay destinos en el select (posiblemente cargados por el backend)
        if (destinoSelect.children.length <= 1) { // Solo hay opción por defecto
            fetch('/api/destinos/')
                .then(response => response.json())
                .then(data => {
                    allDestinos = data;
                    // Limpiar opciones existentes
                    destinoSelect.innerHTML = '<option value="" selected disabled>Seleccione un Destino</option>';
                    // Añadir nuevas opciones
                    data.forEach(destino => {
                        const option = document.createElement('option');
                        option.value = destino.id;
                        option.textContent = destino.nombre;
                        destinoSelect.appendChild(option);
                    });
                })
                .catch(error => console.error('Error cargando destinos:', error));
        } else {
            // Si ya hay opciones, extraerlas a allDestinos
            allDestinos = Array.from(destinoSelect.children).slice(1).map(option => ({
                id: option.value,
                nombre: option.textContent
            }));
        }
    }

    // Cargar destinos al iniciar
    loadDestinations();

    // Agregar evento para manejar selección de medios de transporte
    const transporteOptions = document.querySelectorAll('.transporte-option');
    transporteOptions.forEach(option => {
        option.addEventListener('change', function() {
            // Lógica para manejar la selección de transporte
            const selectedTransportes = Array.from(transporteOptions)
                .filter(opt => opt.checked)
                .map(opt => opt.value);

            console.log('Transportes seleccionados:', selectedTransportes);

            // Si se selecciona transporte aéreo, mostrar un mensaje o pre-cargar información
            if (selectedTransportes.includes('aereo')) {
                console.log('Transporte aéreo seleccionado - Se cargarán datos de vuelos');
                // Aquí se puede agregar lógica para pre-cargar información de vuelos
            } else {
                console.log('Otros medios de transporte seleccionados');
            }
        });
    });

    // Función para calcular la cotización
    function calculateQuotation(e) {
        e.preventDefault();

        // Crear FormData manualmente para tener control sobre los valores
        const formData = new FormData();

        // Agregar todos los campos del formulario
        const formElements = quotationForm.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            if (element.name && element.value) {
                if (element.type === 'checkbox' && element.checked) {
                    formData.append(element.name, element.value);
                } else if (element.type !== 'checkbox') {
                    formData.append(element.name, element.value);
                }
            }
        });

        // Agregar CSRF token si no existe
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken.value);
        }

        // Enviar solicitud al servidor
        fetch('/api/calcular-cotizacion/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const detalle = data.detalle;

                // Mostrar resultados
                resultOrigen.textContent = detalle.origen;
                resultDestination.textContent = detalle.destino;
                resultFechaInicio.textContent = detalle.fecha_inicio;
                resultFechaFin.textContent = detalle.fecha_fin;
                resultTotalPax.textContent = detalle.total_pax;

                // Mostrar desglose de pasajeros
                resultPaxDetails.textContent = `Adultos: ${detalle.desglose_pax.adultos}, Niños: ${detalle.desglose_pax.ninios}, Bebés: ${detalle.desglose_pax.bebes}, Adultos Mayores: ${detalle.desglose_pax.adultos_mayores}, Estudiantes: ${detalle.desglose_pax.estudiantes}`;

                resultUtilidad.textContent = detalle.porcentajes.utilidad;

                // Mostrar precios por pax
                priceHospedajePax.textContent = detalle.precios_por_pax.hospedaje.toFixed(2);
                priceTransportePax.textContent = detalle.precios_por_pax.transporte.toFixed(2);
                priceAlimentacionPax.textContent = detalle.precios_por_pax.alimentacion.toFixed(2);
                priceSeguroPax.textContent = detalle.precios_por_pax.seguro.toFixed(2);

                // Mostrar totales
                totalHospedaje.textContent = detalle.totales.hospedaje.toFixed(2);
                totalTransporte.textContent = detalle.totales.transporte.toFixed(2);
                totalAlimentacion.textContent = detalle.totales.alimentacion.toFixed(2);
                totalSeguro.textContent = detalle.totales.seguro.toFixed(2);

                // Mostrar impuestos y utilidad
                ivaHospedaje.textContent = detalle.totales.iva_hospedaje.toFixed(2);
                ivaOtros.textContent = (detalle.totales.iva - detalle.totales.iva_hospedaje).toFixed(2); // IVA otros servicios
                subtotalConIva.textContent = detalle.totales.subtotal_con_iva.toFixed(2);
                utilidadPorcentaje.textContent = detalle.porcentajes.utilidad;
                montoUtilidad.textContent = detalle.totales.utilidad.toFixed(2);

                // Mostrar total final y precio por pax
                totalFinal.textContent = detalle.totales.total.toFixed(2);
                precioPorPax.textContent = detalle.precios_por_pax.total.toFixed(2);

                // Mostrar resultados
                quoteResult.style.display = 'block';
            } else {
                // Mostrar mensaje más detallado
                let errorMessage = 'Error en la cotización: ';

                if (data.error) {
                    errorMessage += data.error;
                } else if (data.errors) {
                    // Si hay errores de validación específicos
                    if (data.errors.destino) {
                        errorMessage += 'Por favor, seleccione un destino válido.';
                    } else if (data.errors.origen) {
                        errorMessage += 'Por favor, ingrese un origen válido.';
                    } else {
                        errorMessage += 'Datos inválidos.';
                    }

                    console.log('Errores de validación:', data.errors);
                } else {
                    errorMessage += 'Datos inválidos.';
                }

                alert(errorMessage);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Hubo un error al calcular la cotización');
        });
    }

    // Agregar evento de envío al formulario
    quotationForm.addEventListener('submit', calculateQuotation);
});