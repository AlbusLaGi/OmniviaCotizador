document.addEventListener('DOMContentLoaded', function() {
    
    function showInvalidCharNotification(element) {
        let notification = element.parentNode.querySelector('.char-notification');
        if (!notification) {
            notification = document.createElement('span');
            notification.className = 'char-notification';
            notification.style.position = 'absolute';
            notification.style.right = '5px';
            notification.style.top = '50%';
            notification.style.transform = 'translateY(-50%)';
            notification.style.backgroundColor = 'rgba(255, 0, 0, 0.7)';
            notification.style.color = 'white';
            notification.style.padding = '2px 8px';
            notification.style.borderRadius = '5px';
            notification.style.fontSize = '0.8em';
            notification.style.zIndex = '10';
            notification.textContent = 'Carácter no válido';
            element.parentNode.style.position = 'relative'; // Needed for absolute positioning of child
            element.parentNode.appendChild(notification);
        }
        
        notification.style.opacity = '1';

        setTimeout(() => {
            notification.style.opacity = '0';
        }, 1500);
    }

    function formatPriceInput(event) {
        const input = event.target;
        let originalValue = input.value;
        let value = originalValue;

        // Allow only digits and a single comma
        value = value.replace(/[^0-9,]/g, (match) => {
            showInvalidCharNotification(input);
            return ''; // Remove invalid character
        });

        // Ensure there is only one comma
        const parts = value.split(',');
        if (parts.length > 2) {
            value = parts[0] + ',' + parts.slice(1).join('');
            showInvalidCharNotification(input);
        }

        // Limit to two decimal places
        if (parts.length > 1) {
            const decimalPart = parts[1];
            if (decimalPart.length > 2) {
                value = parts[0] + ',' + decimalPart.substring(0, 2);
            }
        }

        // Update the input value if it has changed
        if (input.value !== value) {
            input.value = value;
        }
    }

    // Use event delegation to handle both existing and dynamically added inputs
    document.body.addEventListener('input', function(event) {
        if (event.target.matches('.price-input')) {
            formatPriceInput(event);
        }
    });

    // Add a global submit listener to all forms
    document.body.addEventListener('submit', function(event) {
        // Check if the event target is a form
        if (event.target.tagName.toLowerCase() === 'form') {
            const form = event.target;
            // Find all price inputs within the submitted form
            form.querySelectorAll('.price-input').forEach(input => {
                // Before submitting, convert comma to period for backend compatibility
                if (input.value) {
                    input.value = input.value.replace(/,/g, '.');
                }
            });
        }
    });
});
