// JavaScript para funcionalidade de zoom na imagem do produto
document.addEventListener('DOMContentLoaded', function() {
    const mainImage = document.querySelector('.main-image');
    const productImg = mainImage.querySelector('img');
    
    if (mainImage && productImg) {
        // Adiciona funcionalidade de zoom ao clicar na imagem
        mainImage.addEventListener('click', function() {
            this.classList.toggle('zoom-active');
            
            // Implementa o movimento da imagem durante o zoom
            if (this.classList.contains('zoom-active')) {
                // Adiciona evento de movimento para controlar a posição da imagem ampliada
                this.addEventListener('mousemove', moveZoomedImage);
            } else {
                // Remove o evento de movimento quando o zoom é desativado
                this.removeEventListener('mousemove', moveZoomedImage);
                // Redefine a posição da imagem
                productImg.style.transformOrigin = 'center center';
            }
        });
        
        // Função para mover a imagem ampliada com base na posição do mouse
        function moveZoomedImage(e) {
            const { left, top, width, height } = this.getBoundingClientRect();
            const x = (e.clientX - left) / width * 100;
            const y = (e.clientY - top) / height * 100;
            
            // Define o ponto de origem da transformação com base na posição do mouse
            productImg.style.transformOrigin = `${x}% ${y}%`;
        }
    }
    
    // Configuração dos botões (pode ser expandido conforme necessário)
    const addToCartBtn = document.querySelector('.btn-add-to-cart');
    const buyNowBtn = document.querySelector('.btn-buy-now');
    
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function() {
            // Implementação da adição ao carrinho
            // Este é um placeholder - você precisará implementar a lógica real
            alert('Produto adicionado ao carrinho!');
        });
    }
    
    if (buyNowBtn) {
        buyNowBtn.addEventListener('click', function() {
            // Implementação da compra direta
            // Este é um placeholder - você precisará implementar a lógica real
            alert('Redirecionando para checkout...');
        });
    }
});

// Função para mostrar o toast
function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    toastMessage.innerHTML = `<i class="fas fa-heart"></i> ${message}`;
    toast.classList.remove('toast-hidden');
    toast.classList.add('toast-visible');

    // Esconde após 3 segundos
    setTimeout(() => {
        toast.classList.remove('toast-visible');
        toast.classList.add('toast-hidden');
    }, 3000);
}
