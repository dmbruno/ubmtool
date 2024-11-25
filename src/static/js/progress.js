document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('emailForm');
    const progressBarContainer = document.getElementById('progressBarContainer');
    const progressBar = document.getElementById('progressBar');

    form.addEventListener('submit', async function (e) {
        e.preventDefault(); // Evita que el formulario haga un submit tradicional

        // Muestra la barra de progreso
        progressBarContainer.style.display = 'block';
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);

        const formData = new FormData(form);

        try {
            const response = await fetch('/mass_email', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                // Conectar con el endpoint de progreso
                const eventSource = new EventSource('/mass_email/progress');
                eventSource.onmessage = function (event) {
                    const progress = parseInt(event.data);
                    progressBar.style.width = `${progress}%`;
                    progressBar.setAttribute('aria-valuenow', progress);
                    progressBar.textContent = `${progress}%`;

                    // Finalizar conexión cuando el progreso sea 100%
                    if (progress === 100) {
                        eventSource.close();
                        progressBar.textContent = "Envío completado!";
                        setTimeout(() => {
                            location.reload(); // Recargar la página después de completar
                        }, 2000);
                    }
                };
            } else {
                const errorText = await response.text();
                console.error("Error del servidor:", errorText);
                alert("Error al procesar el envío. Revisa la consola para más detalles.");
            }
        } catch (error) {
            console.error("Error al enviar los correos:", error);
            progressBarContainer.style.display = 'none'; // Oculta la barra en caso de error
        }
    });
});