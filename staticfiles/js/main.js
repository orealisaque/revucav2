// Inicializa o Swiper
const swiper = new Swiper('.swiper-container', {
    loop: true,
    pagination: {
        el: '.swiper-pagination',
        clickable: true
    },
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev'
    }
});

// Função para abrir o modal
function openAnuncioModal(anuncio) {
    const modal = document.getElementById('anuncioModal');
    const swiperWrapper = modal.querySelector('.swiper-wrapper');
    
    // Limpa fotos anteriores
    swiperWrapper.innerHTML = '';
    
    // Adiciona as fotos ao carrossel
    anuncio.fotos.forEach(foto => {
        swiperWrapper.innerHTML += `
            <div class="swiper-slide">
                <img src="${foto.url}" alt="" class="w-full h-full object-cover">
            </div>
        `;
    });
    
    // Atualiza informações
    modal.querySelector('#modalTitulo').textContent = anuncio.titulo;
    modal.querySelector('#modalPreco').textContent = `R$ ${anuncio.preco}/hora`;
    modal.querySelector('#modalLocalizacao').textContent = anuncio.cidade;
    modal.querySelector('#modalDescricao').textContent = anuncio.descricao;
    
    // Atualiza link do WhatsApp
    const whatsappLink = modal.querySelector('#modalWhatsapp');
    whatsappLink.href = `https://wa.me/${anuncio.whatsapp}?text=Olá, vi seu anúncio no site`;
    
    // Mostra o modal
    modal.classList.remove('hidden');
    document.body.classList.add('modal-open');
    
    // Atualiza o Swiper
    swiper.update();
} 