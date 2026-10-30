// Validações no lado do cliente, complementares às validações do servidor

document.addEventListener('DOMContentLoaded', function () {
    // Copia o valor da caixa única de quantidade para o campo escondido
    // do formulário correspondente (entrada ou saída) antes de enviar.
    document.querySelectorAll('.form-mov').forEach(function (form) {
        form.addEventListener('submit', function (evento) {
            const linha = form.closest('tr');
            const inputVisivel = linha.querySelector('.input-mov');
            const campoEscondido = form.querySelector('.qtd-hidden');

            const valor = inputVisivel.value;

            if (!valor || Number(valor) <= 0) {
                evento.preventDefault();
                alert('Informe uma quantidade válida antes de confirmar.');
                inputVisivel.focus();
                return;
            }

            campoEscondido.value = valor;
        });
    });

    // Validação genérica de valores negativos em formulários de cadastro/edição
    const formulario = document.querySelector('form:not(.form-mov)');
    if (!formulario) return;

    formulario.addEventListener('submit', function (evento) {
        const camposNumericos = formulario.querySelectorAll('input[type="number"]:not(.qtd-hidden)');

        for (const campo of camposNumericos) {
            if (campo.value !== '' && Number(campo.value) < 0) {
                evento.preventDefault();
                alert('Valores negativos não são permitidos em: ' + campo.name);
                campo.focus();
                return;
            }
        }
    });
});