from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Residuo,Deposito,User

CATEGORIA_CHOICES = [
    ('', 'Selecione uma categoria'),
    ('Metal', 'Metal'),
    ('Papel', 'Papel'),
    ('Plástico', 'Plástico'),
]

class LoginForm(forms.Form):
    username = forms.CharField(label='Usuário',
        widget=forms.TextInput(attrs={'class': 'form-control input-custom'})
    )
    password = forms.CharField(label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control input-custom'})
    )

class ResiduoForm(forms.ModelForm):
    
    class Meta:
        model = Residuo
        fields = ['residuo_descricao', 'residuo_formula_quimica', 'residuo_categoria', 'residuo_massa', 'residuo_densidade']
        labels = {
            'residuo_descricao': 'Descrição', 
            'residuo_formula_quimica': 'Fórmula Química', 
            'residuo_categoria': 'Categoria',
            'residuo_massa': 'Massa (kg)',
            'residuo_densidade': 'Densidade (kg/dm³)',
        }
        widgets = {
            'residuo_descricao': forms.TextInput(attrs={'class': 'form-control', 'autofocus': 'autofocus'}),
            'residuo_formula_quimica': forms.TextInput(attrs={'class':'form-control'}), 
            'residuo_categoria': forms.Select(choices=CATEGORIA_CHOICES, attrs={'class': 'form-control'}),
            'residuo_massa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'residuo_densidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'})
        }

class DepositoForm(forms.ModelForm):
    class Meta:
        model = Deposito
        fields = ['deposito_descricao', 'residuo', 'deposito_volume']
        labels = {
            'deposito_descricao': 'Descrição', 
            'residuo': 'Resíduo',
            'deposito_volume': 'Volume', 
        }
        widgets = {
            'deposito_descricao': forms.TextInput(attrs={'class': 'form-control', 'autofocus': 'autofocus'}),
            'residuo': forms.Select(attrs={'class': 'form-control'}),
            'deposito_volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
        }
 
class CadastroForm(forms.ModelForm):
    confirme_senha = forms.CharField(label='Confirme a Senha', widget=forms.PasswordInput(attrs={'class': 'form-control input-custom'}))
    class Meta:
        model = User  # Use seu modelo de usuário aqui
        fields = ['user_cnpj', 'user_nome_fantasia', 'user_razao_social', 'user_endereco', 'user_telefone', 'user_email',  'user_login', 'user_password']
        labels = {
            'user_cnpj': 'CNPJ',
            'user_nome_fantasia': 'Nome Fantasia',
            'user_razao_social':'Razão Social',
            'user_endereco': 'Endereço',
            'user_telefone': 'Telefone',
            'user_email': 'Email',
            'user_login': 'Login',
            'user_password': 'Senha',
        }
        widgets = {
            'user_cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ'}),
            'user_nome_fantasia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Fantasia'}),
            'user_razao_social': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razão Social'}),
            'user_endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Endereço'}),
            'user_telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'}),
            'user_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'user_login': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Login'}),
            'user_password': forms.PasswordInput(attrs={'class': 'form-control input-custom'}),
        }

    perfil = forms.ChoiceField(
        label='Perfil',
        choices=[
            (False, 'Gerador de Resíduos'),
            (True, 'Coletor de Resíduos'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("user_password")
        confirme_senha = cleaned_data.get("confirm_password")

        if senha and confirme_senha and senha != confirme_senha:
            raise forms.ValidationError("As senhas não coincidem.")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_password = self.cleaned_data['user_password']  # Armazena a senha
        if commit:
            user.save()
        return user