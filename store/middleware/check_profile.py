from django.shortcuts import redirect
from django.urls import reverse

class CheckProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # Caminhos públicos onde não há necessidade de perfil completo
        self.allowed_paths = [
            reverse('store:home'),
            reverse('store:product_list'),
            reverse('store:login'),
            reverse('store:register'),
            reverse('store:logout'),
        ]

    def __call__(self, request):
        # Libera se o caminho não exige perfil completo
        if any(request.path.startswith(path) for path in self.allowed_paths):
            return self.get_response(request)

        # Aplica verificação só para usuários logados
        if request.user.is_authenticated:
            try:
                perfil = request.user.perfil
                if not perfil.telefone or not perfil.endereco:
                    request.session['next'] = request.path
                    return redirect('store:register')
            except:
                request.session['next'] = request.path
                return redirect('store:register')

        return self.get_response(request)
