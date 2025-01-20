document.addEventListener('DOMContentLoaded', function() {
    const estadoSelect = document.getElementById('id_estado');
    const cidadeSelect = document.getElementById('id_cidade');

    if (estadoSelect && cidadeSelect) {
        estadoSelect.addEventListener('change', function() {
            const estadoId = this.value;
            
            cidadeSelect.innerHTML = '<option value="">---------</option>';
            
            if (estadoId) {
                fetch(`/users/cidades/${estadoId}/`)
                    .then(response => response.json())
                    .then(data => {
                        data.forEach(cidade => {
                            const option = new Option(cidade.nome, cidade.id);
                            cidadeSelect.add(option);
                        });
                    });
            }
        });
    }
}); 