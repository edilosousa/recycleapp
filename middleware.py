from django.shortcuts import redirect

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Rotas que podem ser acessadas sem estar logado
        public_routes = ['/']  # Adicione outras rotas públicas aqui

        # Se o usuário não estiver logado e tentar acessar uma rota restrita
        if not request.session.get('user_id') and request.path not in public_routes:
            return redirect('login')  # Redireciona para a página de login
        
        response = self.get_response(request)
        return response
