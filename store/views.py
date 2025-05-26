from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch
from .models import Category, Product, Perfil
from .forms import RegistroForm, PerfilForm

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import logout 
from django.contrib import messages
from .models import Product, CartItem

from django.contrib.auth import login
from django.views.decorators.csrf import requires_csrf_token
from .models import Favorite
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate





def home(request):
    # Otimização com prefetch_related e select_related
    categories = Category.objects.prefetch_related(
        Prefetch('products', queryset=Product.objects.filter(available=True).order_by('-created'))
    ).all()

    # Novos produtos (últimos 6)
    new_products = Product.objects.filter(available=True).select_related('category').order_by('-created')

    # Todos os produtos (12 mais recentes)
    all_products = Product.objects.filter(available=True).select_related('category').order_by('-created')

    context = {
        'categories': categories,
        'new_products': new_products,
        'all_products': all_products,
    }
    return render(request, 'store/home.html', context)

def product_list(request, category_slug=None):
    """View para listagem de produtos por categoria"""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True).order_by('-created')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, available=True)
    else:
        products = Product.objects.filter(featured=True)
    
    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
    })

def product_detail(request, product_slug):
    """View para detalhes do produto + produtos relacionados"""
    product = get_object_or_404(Product, slug=product_slug, available=True)
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id).order_by('?')[:4]  # Random order

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Redireciona para 'next' ou para a página anterior
                next_url = request.POST.get('next') or request.session.pop('previous_page', None) or 'store:home'
                return redirect(next_url)
        messages.error(request, "Usuário ou senha inválidos.")
    else:
        # Guarda a página atual antes do login
        request.session['previous_page'] = request.META.get('HTTP_REFERER', '/')
        form = AuthenticationForm()
    
    return render(request, 'store/login.html', {
        'form': form,
        'next': request.GET.get('next', '')  # Passa o parâmetro next para o template
    })

# store/views.py
def register_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)  # Adicionado request.FILES
        if form.is_valid():
            user = form.save()
            
            # Cria perfil apenas se não existir
            if not hasattr(user, 'perfil'):
                Perfil.objects.create(
                    usuario=user,
                    telefone=form.cleaned_data.get('telefone'),
                    endereco=form.cleaned_data.get('endereco'),
                    foto=form.cleaned_data.get('foto')  # Adiciona a foto se existir
                )
            
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso!")
            
            # Redirecionamento inteligente
            next_url = request.POST.get('next') or request.session.pop('previous_page', None) or 'store:home'
            return redirect(next_url)
    else:
        # Guarda a página atual antes do registro
        request.session['previous_page'] = request.META.get('HTTP_REFERER', '/')
        form = RegistroForm()
    
    return render(request, 'store/register.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })

@login_required(login_url='store:login')
def perfil_view(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    cart_items = request.user.cart_items.select_related('product')
    favorites = request.user.favorites.select_related('product')
    pedidos = request.user.pedidos.all().prefetch_related('itens')  # Adicionado

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('store:perfil')
    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'store/perfil.html', {
        'form': form,
        'cart_items': cart_items,
        'favorites': favorites,
        'pedidos': pedidos,  # Adicionado
        'total_carrinho': sum(item.product.price * item.quantity for item in cart_items),
    })


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    
    
    # Calcula o total de cada item e o geral
    for item in cart_items:
        item.total_item = item.product.price * item.quantity  # Total por item
    
    total_geral = sum(item.total_item for item in cart_items)  # Total do carrinho
    
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total_geral
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        item.quantity += 1
        item.save()
        messages.success(request, f"Quantidade de {product.name} atualizada!")
    else:
        messages.success(request, f"{product.name} adicionado ao carrinho!")
    return redirect('store:cart') 

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
        messages.info(request, f"Quantidade de {item.product.name} reduzida.")
    else:
        item.delete()
        messages.warning(request, f"{item.product.name} removido do carrinho.")
    return redirect('store:cart') 

@login_required
def delete_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.warning(request, f"{item.product.name} removido do carrinho.")
    return redirect('store:cart') 

@login_required
def checkout_view(request):
    return render(request, 'store/checkout.html') 

@login_required
def logout_view(request):
    logout(request)
    return redirect('store:home')


@requires_csrf_token  # Permite que a view seja chamada mesmo em erros CSRF
def csrf_failure_view(request, reason=""):
    return render(request, 'store/csrf_error.html', status=403)


@login_required
def add_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f"{product.name} adicionado aos favoritos!")
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))

@login_required
def remove_favorite(request, product_id):
    favorite = get_object_or_404(Favorite, user=request.user, product_id=product_id)
    favorite.delete()
    messages.warning(request, f"{favorite.product.name} removido dos favoritos!")
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))