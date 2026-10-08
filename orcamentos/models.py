from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=10, decimal_places=2)  # Suporta até 99.999.999,99

    def __str__(self):
        return self.nome

class ImagemProduto(models.Model):
    produto = models.ForeignKey(Produto, related_name='imagens', on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='produtos/')

    def __str__(self):
        return f"Imagem de {self.produto.nome}"

class Orcamento(models.Model):
    cliente_nome = models.CharField(max_length=100)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    data = models.DateTimeField(auto_now_add=True)

    def valor_total(self):
        return self.produto.preco * self.quantidade

    def __str__(self):
        return f"Orçamento de {self.cliente_nome}"
