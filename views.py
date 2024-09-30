from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout,authenticate, login as auth_login
from django.contrib.auth.hashers import make_password,check_password  
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Prefetch,Sum
from django.db.models.functions import TruncMonth
from itertools import groupby
from .forms import DepositoForm, LoginForm, CadastroForm
from .models import Solicitacao,Residuo,Deposito,User
from .forms import ResiduoForm

def login(request):
    form = LoginForm()  # Inicialize o formulário de login aqui
    cadastro_form = CadastroForm()  # Inicialize o formulário de cadastro aqui

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'login':
            form = LoginForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                try:
                    user = User.objects.get(user_login=username)
                    print(f"Usuário encontrado: {user}")
                    if check_password(password, user.user_password):
                        request.session['user_id'] = user.user_id
                        auth_login(request, user)
                        if user.user_parceiro:
                            return redirect('parceiro_coletor')
                        else:
                            return redirect('dashboard')
                    else:
                        messages.error(request, "Usuário ou senha inválidos.")
                except User.DoesNotExist:
                    messages.error(request, "Usuário ou senha inválidos.")
            else:
                print(form.errors)
                messages.error(request, "Erro na validação do formulário.")

        elif form_type == 'cadastro':
            cadastro_form = CadastroForm(request.POST)
            if cadastro_form.is_valid():
                new_user_cnpj = cadastro_form.cleaned_data['user_cnpj']
                new_user_razao_social = cadastro_form.cleaned_data['user_razao_social']
                new_user_nome_fantasia = cadastro_form.cleaned_data['user_nome_fantasia']
                new_user_login = cadastro_form.cleaned_data['user_login']
                new_user_endereco = cadastro_form.cleaned_data['user_endereco']
                new_user_telefone = cadastro_form.cleaned_data['user_telefone']
                new_user_email = cadastro_form.cleaned_data['user_email']
                new_user_password = cadastro_form.cleaned_data['user_password']
                new_user_parceiro = cadastro_form.cleaned_data['perfil']
                hashed_password = make_password(new_user_password)
                
                new_user = User(
                    user_cnpj=new_user_cnpj,
                    user_nome_fantasia=new_user_nome_fantasia,
                    user_razao_social=new_user_razao_social,
                    user_endereco=new_user_endereco,
                    user_telefone=new_user_telefone,
                    user_email=new_user_email,
                    user_login=new_user_login,
                    user_password=hashed_password,
                    user_parceiro=new_user_parceiro,
                )
                
                new_user.save()
                return JsonResponse({'status': 'success', 'message': 'Usuário cadastrado com sucesso!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Não foi possível cadastrar o usuário!'})

    return render(request, 'recycleapp/login.html', {
        'form': form,
        'cadastro_form': cadastro_form
    })
    
def logout_view(request):
    request.session.flush()  # Remove todas as chaves da sessão
    logout(request)
    return redirect('login')
    
def dashboard(request):
    user_id = request.session.get('user_id')
    usuario = User.objects.get(user_id=user_id) if user_id else None

    # Filtra os resíduos do usuário atual
    residuos = Residuo.objects.filter(user=usuario)
    depositos = Deposito.objects.filter(user=usuario)

    # Calcula a porcentagem ocupada em cada depósito
    for deposito in depositos:
        volume_residuo = deposito.residuo.residuo_massa / deposito.residuo.residuo_densidade
        porcentagem_ocupada = (volume_residuo / deposito.deposito_volume) * 100
        deposito.porcentagem_restante = round(porcentagem_ocupada, 2)

    # Calcula a massa total para cada categoria
    categorias = ['Papel', 'Metal', 'Plástico']
    total_massa = {categoria: round(residuos.filter(residuo_categoria=categoria).aggregate(Sum('residuo_massa'))['residuo_massa__sum'] or 0, 2) for categoria in categorias}

    
    
    # Agrupa os resíduos por mês
    # residuos_por_mes = Residuo.objects.annotate(mes=TruncMonth('residuo_data')).values('mes').annotate(total_massa=Sum('residuo_massa'))
    residuos_por_mes = residuos.annotate(mes=TruncMonth('residuo_data')).values('mes').annotate(total_massa=Sum('residuo_massa'))
    massa_por_mes = defaultdict(float)
    for residuo in residuos_por_mes:
        mes_formatado = residuo['mes'].strftime('%Y-%m')
        # Converte 'total_massa' para float antes de somar
        massa_por_mes[mes_formatado] += float(residuo['total_massa'])

    # Passa os dados para o template
    return render(request, 'recycleapp/dashboard.html', {
        'usuario': usuario,
        'categorias': categorias,
        'total_massa': total_massa,
        'depositos': depositos,
        'massa_por_mes': dict(massa_por_mes),  # Certifique-se de converter defaultdict para dict
    })

def residuo(request):
    form = ResiduoForm()
    user_id = request.session.get('user_id')
    usuario = User.objects.get(user_id=user_id) if user_id else None
    residuos = Residuo.objects.filter(user_id=user_id) if user_id else Residuo.objects.none()
    return render(request,'recycleapp/residuo.html',{
        'residuos': residuos,
        'form': form,
        'usuario': usuario
    })

def add_residuo(request):
    if request.method == 'POST':
        form = ResiduoForm(request.POST)
        if form.is_valid():
            new_residuo_descricao = form.cleaned_data['residuo_descricao']
            new_residuo_formula_quimica = form.cleaned_data['residuo_formula_quimica']
            new_residuo_categoria = form.cleaned_data['residuo_categoria']
            new_residuo_massa = form.cleaned_data['residuo_massa']
            new_residuo_densidade = form.cleaned_data['residuo_densidade']
            user_id = request.session.get('user_id')
            usuario = User.objects.get(user_id=user_id)
            
            new_residuo = Residuo(
                residuo_descricao = new_residuo_descricao, 
                residuo_formula_quimica = new_residuo_formula_quimica,
                residuo_categoria = new_residuo_categoria,
                residuo_massa = new_residuo_massa,
                residuo_densidade = new_residuo_densidade,
                user=usuario
            )

            new_residuo.save()
            if new_residuo:
                return JsonResponse({'status': 'success', 'message': 'Resíduo cadastrado com sucesso!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Não foi possível cadastrar o resíduo!'})
    
def edit_residuo(request):
    if request.method == 'POST':
        id_residuo = request.POST.get('residuo_id')
        residuo = get_object_or_404(Residuo, residuo_id=id_residuo)
        
        descricao = request.POST.get('residuo_descricao')
        formula_quimica = request.POST.get('residuo_formula_quimica')
        categoria = request.POST.get('residuo_categoria')
        massa = request.POST.get('residuo_massa')
        densidade = request.POST.get('residuo_densidade')

        residuo.residuo_descricao = descricao
        residuo.residuo_formula_quimica = formula_quimica
        residuo.residuo_categoria = categoria
        residuo.residuo_massa = massa
        residuo.residuo_densidade = densidade
        residuo.save()

        if residuo:
            return JsonResponse({'status': 'success', 'message': 'Resíduo alterado com sucesso!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Não foi possível alterar o resíduo!'})
    return HttpResponse('Método não permitido', status=405)

def delete_residuo(request):
    if request.method == 'POST':
        id_residuo = request.POST.get('residuo_id')
        residuo = get_object_or_404(Residuo, residuo_id=id_residuo)
        residuo.delete()
        if residuo:
            return JsonResponse({'status': 'success', 'message': 'Resíduo exclúido com sucesso!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Não foi possível excluir o resíduo!'})
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)

def deposito(request):
    user_id = request.session.get('user_id')
    depositos = Deposito.objects.filter(user=user_id) if user_id else Deposito.objects.none()
    residuos = Residuo.objects.filter(user=user_id) if user_id else Residuo.objects.none()
    form = DepositoForm()
    usuario = User.objects.get(user_id=user_id) if user_id else None
    return render(request,'recycleapp/deposito.html', {'depositos': depositos, 'residuos': residuos, 'form': form, 'usuario': usuario})

def add_deposito(request):
    if request.method == 'POST':
        form = DepositoForm(request.POST)
        if form.is_valid():
            user_id = request.session.get('user_id')
            new_deposito_descricao = form.cleaned_data['deposito_descricao']
            new_deposito_volume = form.cleaned_data['deposito_volume']
            new_residuo = form.cleaned_data['residuo']
            usuario = User.objects.get(user_id=user_id)

            # Obtenha a quantidade em kg do resíduo
            residuo_massa = new_residuo.residuo_massa  # Certifique-se de que este campo existe
            residuo_densidade = new_residuo.residuo_densidade  # Certifique-se de que este campo existe
            
            print("MASSA",residuo_massa)

            # Calcule o volume necessário para o resíduo
            volume_necessario = round(residuo_massa / residuo_densidade ,2) # Volume em dm³
            

            # Verifique se o volume do depósito é suficiente
            if new_deposito_volume < volume_necessario:
                # Retornar o mesmo template com o formulário e os erros
                return JsonResponse({
                        'status': 'error',
                        'message': 'O volume do depósito não é suficiente para armazenar o resíduo selecionado.',
                        'volume_necessario': volume_necessario
                })

            else:
                # Se o volume for suficiente, crie o novo depósito
                new_deposito = Deposito(
                    deposito_descricao=new_deposito_descricao, 
                    deposito_volume=new_deposito_volume,
                    residuo=new_residuo,
                    user=usuario,
                )

                new_deposito.save()
                return redirect('deposito')
    else:
        form = DepositoForm()  # Cria um novo formulário se não for um POST

    return render(request, 'recycleapp/deposito.html', {'form': form})  # Retorna o formulário

def edit_deposito(request):
    if request.method == 'POST':
        id_deposito = request.POST.get('deposito_id')
        deposito = get_object_or_404(Deposito, deposito_id=id_deposito)
        descricao = request.POST.get('deposito_descricao')
        volume = request.POST.get('deposito_volume')
        residuo_id = request.POST.get('residuo')

        # Verificar se o residuo_id foi enviado corretamente
        if residuo_id:
            try:
                residuo = Residuo.objects.get(residuo_id=residuo_id)
            except Residuo.DoesNotExist:
                return HttpResponse(f'Residuo com ID {residuo_id} não existe', status=404)

            deposito.deposito_descricao = descricao
            deposito.deposito_volume = volume
            deposito.residuo = residuo
            deposito.save()

            if deposito:
                return JsonResponse({'status': 'success', 'message': 'Depósito alterado com sucesso!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Não foi possível alterar o depósito!'})
        else:
            return HttpResponse('ID do residuo não fornecido', status=400)
    
    return HttpResponse('Método não permitido', status=405)

def delete_deposito(request):
    if request.method == 'POST':
        id_deposito= request.POST.get('deposito_id')
        deposito = get_object_or_404(Deposito, deposito_id=id_deposito)
        deposito.delete()
        if deposito:
            return JsonResponse({'status': 'success', 'message': 'Depósito exclúido com sucesso!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Não foi possível excluir o depósito!'})
    return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)

def parceiro(request):
    user_id = request.session.get('user_id')
    usuario = User.objects.get(user_id=user_id) if user_id else None
    parceiros = User.objects.filter(user_parceiro=True)
    solicitacoes = Solicitacao.objects.filter(user_gerador__user_id=user_id)
    solicitacoes_unicas = []
    for key, group in groupby(solicitacoes, lambda x: x.user_parceiro.user_cnpj):
        solicitacoes_unicas.append(next(group))  # Pega apenas o primeiro de cada grupo
    return render(request,'recycleapp/parceiro.html',{'usuario': usuario,'parceiros': parceiros,'solicitacoes_unicas': solicitacoes_unicas, 'solicitacoes':solicitacoes})

def parceiro_coletor(request):
    user_id = request.session.get('user_id')
    usuario = User.objects.get(user_id=user_id) if user_id else None
    
    # Prefetch resíduos e solicitações
    residuos_prefetch = Prefetch('residuo_set', queryset=Residuo.objects.all(), to_attr='residuos_fabricados')
    solicitacoes_prefetch = Prefetch('solicitacoes_gerador', queryset=Solicitacao.objects.all(), to_attr='solicitacoes_geradas')

    # Obter os produtores de resíduos (não parceiros)
    produtores_residuos = User.objects.filter(user_parceiro=False).prefetch_related(residuos_prefetch, solicitacoes_prefetch)
    
    return render(request, 'recycleapp/parceiro-coletor.html', {
        'usuario': usuario,
        'produtores_residuos': produtores_residuos,
    })

def salvar_solicitacao(request):
    if request.method == "POST":
        # ID do parceiro (usuário logado) que está solicitando a parceria
        user_parceiro_id = request.session.get('user_id')
        user_parceiro = User.objects.get(user_id=user_parceiro_id)
        
        # IDs dos resíduos selecionados
        residuos_selecionados = request.POST.getlist('residuos_selecionados')
        mensagens_erro = []
        mensagens_sucesso = []

        # Iterar sobre cada resíduo selecionado e salvar na tabela de solicitação
        for residuo_id in residuos_selecionados:
            residuo = Residuo.objects.get(residuo_id=residuo_id)
            user_gerador = residuo.user  # Gerador é o usuário associado ao resíduo
            
            solicitacao_existente = Solicitacao.objects.filter(
                residuo=residuo,
                user_parceiro=user_parceiro
            ).exists()
            
            if solicitacao_existente:
                mensagens_erro.append(f'O resíduo {residuo.residuo_descricao} já foi solicitado por você.')
            else:
                # Criar uma nova solicitação
                solicitacao = Solicitacao.objects.create(
                    residuo=residuo,
                    user_parceiro=user_parceiro,
                    user_gerador=user_gerador,
                    solicitacao_aceite=2  # Status "Pendente"
                )
                solicitacao.save()
                mensagens_sucesso.append(f'Solicitação para o resíduo {residuo.residuo_descricao} enviada com sucesso.')
            
            if mensagens_erro:
                return JsonResponse({'status': 'error', 'errors': mensagens_erro})
            else:
                return JsonResponse({'status': 'success', 'messages': mensagens_sucesso})
    # Em caso de erro, renderize de volta a página original
    return render(request, 'parceiro_coletor')

def aprovar_solicitacoes(request):
    if request.method == "POST":
        solicitacoes = {
            key: request.POST[key]
            for key in request.POST if key.startswith('solicitacoes_ids')
        }
        # Processar cada solicitação e atualizar o status
        for key, value in solicitacoes.items():
            try:
                # Divide o ID da solicitação e a ação (1 ou 3)
                solicitacao_id_str, acao = value.split('|')
                solicitacao_id_int = int(solicitacao_id_str)

                # Atualiza o status da solicitação com base na ação
                if acao == '1':  # Aprovado
                    Solicitacao.objects.filter(solicitacao_id=solicitacao_id_int).update(solicitacao_aceite=1)
                elif acao == '3':  # Reprovado
                    Solicitacao.objects.filter(solicitacao_id=solicitacao_id_int).update(solicitacao_aceite=3)

            except (ValueError, IndexError):
                # Captura e ignora valores inválidos
                continue

        return redirect('parceiro')

    return HttpResponse("Método não permitido", status=405)

def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)