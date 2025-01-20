document.addEventListener('DOMContentLoaded', function() {
    const estadoSelect = document.getElementById('id_estado');
    const cidadeSelect = document.getElementById('id_cidade');

    if (estadoSelect && cidadeSelect) {
        estadoSelect.addEventListener('change', function() {
            const estadoId = this.value;
            if (estadoId) {
                fetch(`/users/get_cidades/?estado_id=${estadoId}`)
                    .then(response => response.json())
                    .then(data => {
                        cidadeSelect.innerHTML = '<option value="">---------</option>';
                        data.forEach(cidade => {
                            const option = new Option(cidade.nome, cidade.id);
                            cidadeSelect.add(option);
                        });
                    });
            } else {
                cidadeSelect.innerHTML = '<option value="">---------</option>';
            }
        });
    }
}); 