from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from PIL import Image, ImageDraw
from io import BytesIO
from django.core.files.base import ContentFile
import random
from django.conf import settings



class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    image = models.ImageField(
        upload_to='categories/', 
        blank=True, 
        null=True,
        verbose_name="Imagem da Categoria"
    )
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(
        Category, 
        related_name='products',
        on_delete=models.CASCADE,
        verbose_name="Categoria"
    )
    name = models.CharField(max_length=200, verbose_name="Nome")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    image = models.ImageField(upload_to='products/', verbose_name="Imagem Principal")
    description = models.TextField(blank=True, verbose_name="Descrição")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Preço"
    )
    is_new = models.BooleanField(default=False, verbose_name="Novo?")
    featured = models.BooleanField(default=False, verbose_name="Destaque?")
    available = models.BooleanField(default=True, verbose_name="Disponível?")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['-created']),
            models.Index(fields=['featured']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])
    

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    )
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    endereco_entrega = models.TextField()
    
    class Meta:
        ordering = ['-data_pedido']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.name} (Pedido #{self.pedido.id})"
    
class Favorite(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Evita favoritos duplicados
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'

    def __str__(self):
        return f"{self.user.username} favoritou {self.product.name}"
    
class CartItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="Usuário"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_products',
        verbose_name="Produto"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'product']),
            models.Index(fields=['created_at']),
        ]
        unique_together = ['user', 'product']  # Evita duplicatas

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity

class Perfil(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name="Usuário"
    )
    telefone = models.CharField(
        max_length=20,
        verbose_name="Telefone",
        blank=True
    )
    endereco = models.TextField(
        verbose_name="Endereço Completo",
        blank=True
    )
    foto = models.ImageField(
        upload_to='perfil_fotos/',
        blank=True,
        null=True,
        verbose_name="Foto de Perfil"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        ordering = ['-criado_em']



    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
    def generate_avatar(self):
        """Gera um avatar geek programaticamente"""
        # Paleta de cores 8-bit (roxo, azul, verde, laranja)
        colors = [
            (142, 68, 173),   # Roxo
            (41, 128, 185),   # Azul
            (39, 174, 96),    # Verde
            (243, 156, 18)    # Amarelo
        ]
        img = Image.new('RGB', (200, 200), color=random.choice(colors))
        draw = ImageDraw.Draw(img)
        
        # Texto centralizado (inicial do username)
        draw.text(
            (100, 100), 
            self.usuario.username[0].upper(), 
            fill=(255, 255, 255),
            font_size=100,
            anchor="mm"
        )
        
        # Salva em memória e atribui ao campo 'foto'
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        self.foto.save(
            f'avatar_{self.usuario.username}.png',
            ContentFile(buffer.getvalue()),
            save=False
        )

    def save(self, *args, **kwargs):
        """Gera avatar automaticamente se não houver foto"""
        if not self.foto:
            self.generate_avatar()
        super().save(*args, **kwargs)

# Signal para criar perfil automaticamente
@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)



