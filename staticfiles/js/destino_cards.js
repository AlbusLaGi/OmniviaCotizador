function selectDestino(destinoId) {
    // Buscar el elemento de datos en cualquiera de las posibles ubicaciones
    const destinoDataElement = document.getElementById('destinos-data-dashboard') || document.getElementById('destinos-data-dataentry');

    if (!destinoDataElement) {
        console.error('No se encontró el elemento con los datos de destinos');
        return;
    }

    const destinosData = JSON.parse(destinoDataElement.textContent);
    const destino = destinosData.find(d => d.id === destinoId);

    if (destino) {
        // Mostrar el contenedor de detalles (usando cualquiera de las posibles IDs)
        const cardContainer = document.getElementById('destino-card-container') || document.getElementById('destino-card-container-dashboard') || document.getElementById('destino-card-container-dataentry');

        if (cardContainer) {
            cardContainer.style.display = 'block';

            // Crear la tarjeta de destino con detalles completos
            let actividadesHtml = '';
            if (destino.actividades && destino.actividades.length > 0) {
                destino.actividades.forEach(atractivo => {
                    actividadesHtml += `
                        <div class="mb-2 p-2 border rounded">
                            <strong>\${atractivo.atractivo_nombre || atractivo.nombre || 'N/A'}</strong> - \${atractivo.tipo_costo || atractivo.tipo_costo || 'N/A'}
                            \${atractivo.tipo_asignacion ? `<small class="text-muted">Tipo: \${atractivo.tipo_asignacion}</small>` : ''}
                            \${atractivo.precios && atractivo.precios.length > 0 ? `
                                <table class="table table-sm mt-1">
                                    <thead>
                                        <tr><th>Descripción</th><th>Alta</th><th>Media</th><th>Baja</th></tr>
                                    </thead>
                                    <tbody>
                                        \${atractivo.precios.map(precio => `
                                            <tr>
                                                <td>\${precio.categoria || 'N/A'}</td>
                                                <td>\${precio.temporada_alta || precio.temporada_alta || '0'}</td>
                                                <td>\${precio.temporada_media || precio.temporada_media || '0'}</td>
                                                <td>\${precio.temporada_baja || precio.temporada_baja || '0'}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            ` : ''}
                        </div>
                    `;
                });
            }

            cardContainer.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h4>\${destino.nombre}</h4>
                    </div>
                    <div class="card-body">
                        <p><strong>Ubicación:</strong> \${destino.ubicacion}</p>
                        <p><strong>Descripción:</strong> \${destino.descripcion}</p>
                        <p><strong>Categoría:</strong> \${destino.categoria}</p>
                        \${actividadesHtml ? \`<p><strong>Atractivos y Puntos de Interés:</strong></p>\${actividadesHtml}\` : ''}
                    </div>
                    <div class="card-footer">
                        <a href="\${destino.update_url}" class="btn btn-primary">Editar</a>
                        <a href="\${destino.delete_url}" class="btn btn-danger" onclick="return confirm('¿Está seguro de que desea eliminar este destino?')">Eliminar</a>
                    </div>
                </div>
            `;
        }
    }
}

// Función para inicializar la funcionalidad de destinos en cualquier página
function initDestinoCards() {
    // Asegurar que la funcionalidad esté disponible en ambas páginas
    console.log('Funcionalidad de destinos inicializada');
}