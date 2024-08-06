
function editarCliente(id) {
    window.location.href = `/edit/${id}`;
    console.log('Editar cliente con ID:', id);
}

function eliminarCliente(id) {
    if (confirm('¿Estás seguro de que deseas eliminar este cliente?')) {
        fetch(`/eliminar_cliente/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Cliente eliminado con éxito');
                    location.reload();
                } else {
                    alert('Hubo un error al eliminar el cliente');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Hubo un error al eliminar el cliente');
            });
    }
}
