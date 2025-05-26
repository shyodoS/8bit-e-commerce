from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, Product
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Perfil
from .models import CartItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image_preview', 'description_short', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_preview', 'product_count')
    search_fields = ('name', 'description')
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Imagem', {
            'fields': ('image', 'image_preview')
        }),
    )
    
    def description_short(self, obj):
        return obj.description[:100] + '...' if obj.description else ''
    description_short.short_description = 'Descrição'
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" style="object-fit: cover;" />')
        return "Sem imagem"
    image_preview.short_description = 'Pré-visualização'
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Nº de Produtos'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'category', 
        'price', 
        'available', 
        'is_new', 
        'featured',
        'image_preview',
        'created_short'
    )
    list_filter = (
        ('category', admin.RelatedOnlyFieldListFilter),
        'available',
        'is_new',
        'featured',
        'created',
    )
    list_editable = ('price', 'available', 'is_new', 'featured')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = (
        'image_preview', 
        'created', 
        'updated',
        'created_short'
    )
    search_fields = ('name', 'description', 'category__name')
    date_hierarchy = 'created'
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'price', 'description')
        }),
        ('Imagem', {
            'fields': ('image', 'image_preview')
        }),
        ('Status', {
            'fields': ('available', 'is_new', 'featured')
        }),
        ('Datas', {
            'fields': ('created', 'updated')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" style="object-fit: cover;" />')
        return "Sem imagem"
    image_preview.short_description = 'Imagem'
    
    def created_short(self, obj):
        return obj.created.strftime('%d/%m/%Y')
    created_short.short_description = 'Criado em'
    
    actions = ['make_available', 'make_unavailable', 'mark_as_new', 'mark_as_featured']
    
    def make_available(self, request, queryset):
        queryset.update(available=True)
    make_available.short_description = "Marcar selecionados como disponíveis"
    
    def make_unavailable(self, request, queryset):
        queryset.update(available=False)
    make_unavailable.short_description = "Marcar selecionados como indisponíveis"
    
    def mark_as_new(self, request, queryset):
        queryset.update(is_new=True)
    mark_as_new.short_description = "Marcar selecionados como novos"
    
    def mark_as_featured(self, request, queryset):
        queryset.update(featured=True)
    mark_as_featured.short_description = "Destacar produtos selecionados"


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('telefone', 'endereco', 'foto', 'criado_em', 'atualizado_em')
    readonly_fields = ('criado_em', 'atualizado_em')

class CustomUserAdmin(UserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'perfil__telefone')

# Primeiro desregistra o admin padrão
admin.site.unregister(User)

# Depois registra a versão customizada
admin.site.register(User, CustomUserAdmin)

# Opcional: admin separado para Perfil
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefone_curto', 'criado_em')
    search_fields = ('usuario__username', 'telefone', 'endereco')
    
    def telefone_curto(self, obj):
        return obj.telefone[:15] if obj.telefone else ''
    telefone_curto.short_description = 'Telefone'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'total_item', 'created_at')
    list_filter = ('user', 'product__category')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('total_item', 'created_at')
    list_select_related = ('user', 'product')
    autocomplete_fields = ['user', 'product']
    date_hierarchy = 'created_at'
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('user', 'product', 'quantity')
        }),
        ('Informações Adicionais', {
            'fields': ('total_item', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def total_item(self, obj):
        return f"R$ {obj.product.price * obj.quantity:.2f}"
    total_item.short_description = 'Total'