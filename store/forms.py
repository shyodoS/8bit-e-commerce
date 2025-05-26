# store/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nome Completo',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Digite seu nome completo'})
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=100,
        required=False
    )
    email = forms.EmailField(required=True)
    telefone = forms.CharField(max_length=20, required=True)
    endereco = forms.CharField(widget=forms.Textarea, required=True)
    foto = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
        help_text='Foto de perfil (opcional)'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'foto', 'telefone', 'endereco']

    def save(self, commit=True):
        user = super().save(commit=commit)
        
        # Cria ou atualiza o perfil
        perfil, created = Perfil.objects.get_or_create(usuario=user)
        perfil.telefone = self.cleaned_data.get('telefone')
        perfil.endereco = self.cleaned_data.get('endereco')
        
        # Salva a foto se foi enviada
        if self.cleaned_data.get('foto'):
            perfil.foto = self.cleaned_data.get('foto')
        
        if commit:
            perfil.save()
        
        return user

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if not telefone.isdigit():
            raise forms.ValidationError("O telefone deve conter apenas números")
        if len(telefone) < 10:
            raise forms.ValidationError("Telefone inválido (inclua DDD)")
        return telefone

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name.split()) < 2:
            raise forms.ValidationError("Por favor, insira seu nome completo")
        return first_name

class PerfilForm(forms.ModelForm):
    foto = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
        help_text='Formatos: JPG, PNG (máx. 2MB)'
    )
    
    class Meta:
        model = Perfil
        fields = ['foto', 'telefone', 'endereco']
        widgets = {
            'endereco': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if not telefone.isdigit():
            raise forms.ValidationError("O telefone deve conter apenas números")
        if len(telefone) < 10:
            raise forms.ValidationError("Telefone inválido (inclua DDD)")
        return telefone