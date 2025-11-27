document.addEventListener('DOMContentLoaded', function() {
    (function($) {
        $(document).ready(function() {
            const tipoSelect = $('#id_Tipo');
            const otroTipoRow = $('.form-row.field-otro_tipo');

            function toggleOtroTipo() {
                if (tipoSelect.val() === 'otros') {
                    otroTipoRow.show();
                } else {
                    otroTipoRow.hide();
                }
            }

            // Initial check
            toggleOtroTipo();

            // Check on change
            tipoSelect.on('change', toggleOtroTipo);
        });
    })(django.jQuery);
});
