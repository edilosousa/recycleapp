from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_cnpj = models.CharField(max_length=18, blank=True, null=True)
    user_nome_fantasia = models.CharField(max_length=255, blank=True, null=True)
    user_razao_social = models.CharField(max_length=255, blank=True, null=True)
    user_endereco = models.CharField(max_length=255, blank=True, null=True)
    user_telefone = models.CharField(max_length=15, blank=True, null=True)
    user_email = models.EmailField(max_length=255, unique=True)
    user_login = models.CharField(max_length=255, unique=True)
    user_password = models.CharField(max_length=255)
    user_parceiro = models.BooleanField(default=False)
    user_status = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tbluser'

    def __str__(self):
        return self.user_login

class Residuo(models.Model):
    residuo_id = models.AutoField(primary_key=True)
    residuo_descricao = models.CharField(max_length=255)
    residuo_formula_quimica = models.CharField(max_length=255)
    residuo_categoria = models.CharField(max_length=50)
    residuo_massa = models.DecimalField(max_digits=10, decimal_places=3)
    residuo_densidade = models.DecimalField(max_digits=10, decimal_places=3)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user')
    residuo_data = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tblresiduo'

    def __str__(self):
        return self.residuo_descricao

class Deposito(models.Model):
    deposito_id = models.AutoField(primary_key=True)
    deposito_descricao = models.CharField(max_length=255)
    residuo = models.ForeignKey(Residuo, on_delete=models.CASCADE)
    deposito_volume = models.DecimalField(max_digits=10, decimal_places=3)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user')

    class Meta:
        db_table = 'tbldeposito'

    def __str__(self):
        return self.deposito_descricao

class Solicitacao(models.Model):
    solicitacao_id = models.AutoField(primary_key=True)
    residuo = models.ForeignKey(Residuo, on_delete=models.CASCADE, db_column='residuo_id')
    user_parceiro = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitacoes_parceiro', db_column='user_parceiro_id')
    user_gerador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitacoes_gerador', db_column='user_gerador_id')
    solicitacao_aceite = models.IntegerField(default=0)

    class Meta:
        db_table = 'tblsolicitacao'

    def __str__(self):
        return f"Solicitação {self.solicitacao_id} - Aceite: {self.solicitacao_aceite}"

