document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.multi-item-carousel');
    if (!carousel) {
        console.log('Carrossel não encontrado');
        return;
    }

    // Elementos do DOM
    const inner = carousel.querySelector('.carousel-inner');
    const products = Array.from(carousel.querySelectorAll('.carousel-product'));
    const prevBtn = carousel.querySelector('.carousel-control.prev');
    const nextBtn = carousel.querySelector('.carousel-control.next');
    
    // Criar o contêiner de indicadores se não existir
    let indicatorsContainer = carousel.querySelector('.carousel-indicators');
    if (!indicatorsContainer) {
        indicatorsContainer = document.createElement('div');
        indicatorsContainer.className = 'carousel-indicators';
        carousel.appendChild(indicatorsContainer);
    }
    
    // Configurações ajustáveis
    const config = {
        itemsPerSlide: 3,       // Valor padrão (será sobrescrito por currentItemsPerSlide)
        autoplayDelay: 2000,
        autoplay: true,
        responsive: {
            992: 3,
            768: 2,
            576: 1
        }
    };
    
    // Estado do carrossel
    let currentSlide = 0;
    let slides = [];
    let autoplayInterval;
    let currentItemsPerSlide = config.itemsPerSlide;

    // Verificar se há produtos
    console.log(`Produtos carregados: ${products.length}`);
    if (products.length > 0) {
        console.log(`Primeiro produto: ${products[0].querySelector('.card-title')?.textContent || 'Nome não encontrado'}`);
    }

    // Inicialização
    initCarousel();

    function initCarousel() {
        if (products.length === 0) {
            showNoProductsMessage();
            return;
        }

        updateItemsPerSlide();
        groupProducts();
        createIndicators();
        setupEvents();
        
        if (config.autoplay) {
            startAutoplay();
        }
        
        console.log(`Carrossel inicializado com ${slides.length} slides, ${currentItemsPerSlide} itens por slide`);
    }

    function showNoProductsMessage() {
        inner.innerHTML = '<div class="no-products-message">Nenhum produto disponível no momento</div>';
        if (prevBtn) prevBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'none';
        if (indicatorsContainer) indicatorsContainer.style.display = 'none';
    }

    function updateItemsPerSlide() {
        const width = window.innerWidth;
        
        if (width <= 576) {
            currentItemsPerSlide = config.responsive[576];
        } else if (width <= 768) {
            currentItemsPerSlide = config.responsive[768];
        } else {
            currentItemsPerSlide = config.responsive[992];
        }
        
        console.log(`Largura da tela: ${width}px, itens por slide: ${currentItemsPerSlide}`);
    }

    function groupProducts() {
        // Guardar os produtos originais antes de manipular o DOM
        const originalProducts = products.map(p => p.cloneNode(true));
        
        // Limpa o conteúdo atual
        inner.innerHTML = '';
        slides = [];
        
        // Se não houver produtos, não há nada para agrupar
        if (originalProducts.length === 0) return;
        
        // Calcula quantos slides serão necessários
        const totalSlides = Math.ceil(originalProducts.length / currentItemsPerSlide);
        console.log(`Agrupando ${originalProducts.length} produtos em ${totalSlides} slides, ${currentItemsPerSlide} por slide`);
        
        // Cria cada slide
        for (let i = 0; i < totalSlides; i++) {
            // Índices dos produtos para este slide
            const startIndex = i * currentItemsPerSlide;
            const endIndex = Math.min(startIndex + currentItemsPerSlide, originalProducts.length);
            
            // Cria o elemento do slide
            const slide = document.createElement('div');
            slide.className = `carousel-slide ${i === 0 ? 'active' : ''}`;
            
            // Adiciona os produtos ao slide
            for (let j = startIndex; j < endIndex; j++) {
                const productClone = originalProducts[j].cloneNode(true);
                slide.appendChild(productClone);
            }
            
            // Adiciona o slide ao carrossel
            inner.appendChild(slide);
            slides.push(slide);
        }
        
        // Atualiza o estado inicial
        currentSlide = 0;
        updateCarousel();
    }

    function createIndicators() {
        if (!indicatorsContainer) return;
        
        indicatorsContainer.innerHTML = '';
        
        // Cria um indicador para cada slide
        for (let i = 0; i < slides.length; i++) {
            const indicator = document.createElement('button');
            indicator.className = `carousel-indicator ${i === currentSlide ? 'active' : ''}`;
            indicator.setAttribute('aria-label', `Ir para slide ${i + 1}`);
            indicator.addEventListener('click', () => {
                console.log('Indicador clicado: slide', i + 1);
                goToSlide(i);
                resetAutoplay();
            });
            indicatorsContainer.appendChild(indicator);
        }
    }

    function updateIndicators() {
        if (!indicatorsContainer) return;
        
        const indicators = indicatorsContainer.querySelectorAll('.carousel-indicator');
        indicators.forEach((indicator, index) => {
            const isActive = index === currentSlide;
            indicator.classList.toggle('active', isActive);
            indicator.setAttribute('aria-current', isActive ? 'true' : 'false');
        });
    }

    function updateCarousel() {
        // Atualiza as classes de visibilidade nos slides
        slides.forEach((slide, index) => {
            if (index === currentSlide) {
                slide.classList.add('active');
                slide.setAttribute('aria-hidden', 'false');
            } else {
                slide.classList.remove('active');
                slide.setAttribute('aria-hidden', 'true');
            }
        });
        
        // Atualiza os indicadores
        updateIndicators();
        
        // Atualiza os controles de navegação
        if (prevBtn) {
            prevBtn.disabled = slides.length <= 1;
            prevBtn.setAttribute('aria-disabled', slides.length <= 1 ? 'true' : 'false');
        }
        
        if (nextBtn) {
            nextBtn.disabled = slides.length <= 1;
            nextBtn.setAttribute('aria-disabled', slides.length <= 1 ? 'true' : 'false');
        }
    }

    function goToSlide(index) {
        // Verifica se o índice é válido
        if (index < 0 || index >= slides.length) {
            console.warn('Índice de slide inválido:', index);
            return;
        }
        
        console.log('Indo para o slide', index + 1);
        
        // Remove a classe 'active' do slide atual
        if (slides[currentSlide]) {
            slides[currentSlide].classList.remove('active');
        }
        
        // Atualiza o slide atual
        currentSlide = index;
        
        // Adiciona a classe 'active' ao novo slide
        slides[currentSlide].classList.add('active');
        
        // Atualiza a exibição
        updateCarousel();
    }

    function nextSlide() {
        if (slides.length === 0) return;
        
        const nextIndex = (currentSlide + 1) % slides.length;
        console.log('Próximo slide:', nextIndex + 1);
        goToSlide(nextIndex);
    }

    function prevSlide() {
        if (slides.length === 0) return;
        
        const prevIndex = (currentSlide - 1 + slides.length) % slides.length;
        console.log('Slide anterior:', prevIndex + 1);
        goToSlide(prevIndex);
    }

    function startAutoplay() {
        console.log('Iniciando autoplay...');
        stopAutoplay();
        autoplayInterval = setInterval(() => {
            console.log('Autoplay: mudando para próximo slide');
            nextSlide();
        }, config.autoplayDelay);
    }

    function stopAutoplay() {
        if (autoplayInterval) {
            console.log('Parando autoplay...');
            clearInterval(autoplayInterval);
            autoplayInterval = null;
        }
    }

    function resetAutoplay() {
        if (config.autoplay) {
            console.log('Reiniciando autoplay...');
            stopAutoplay();
            startAutoplay();
        }
    }

    function setupEvents() {
        // Controles de navegação
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                console.log('Botão anterior clicado');
                prevSlide();
                resetAutoplay();
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                console.log('Botão próximo clicado');
                nextSlide();
                resetAutoplay();
            });
        }
        
        // Eventos de autoplay
        carousel.addEventListener('mouseenter', () => {
            console.log('Mouse entrou no carrossel - pausando autoplay');
            stopAutoplay();
        });
        
        carousel.addEventListener('mouseleave', () => {
            if (config.autoplay) {
                console.log('Mouse saiu do carrossel - retomando autoplay');
                startAutoplay();
            }
        });
        
        // Eventos de toque para mobile
        carousel.addEventListener('touchstart', stopAutoplay);
        carousel.addEventListener('touchend', () => {
            if (config.autoplay) {
                console.log('Toque finalizado - retomando autoplay em', config.autoplayDelay, 'ms');
                setTimeout(startAutoplay, config.autoplayDelay);
            }
        });
        
        // Redimensionamento da janela
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                console.log('Redimensionamento detectado - recalculando...');
                updateItemsPerSlide();
                groupProducts();
                updateCarousel();
            }, 200);
        });
    }
});