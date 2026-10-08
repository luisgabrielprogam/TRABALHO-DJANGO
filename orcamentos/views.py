import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from .models import Produto, ImagemProduto, Orcamento

# --- CRUD PRODUTOS ---
def lista_produtos(request):
    produtos = Produto.objects.all()
    return render(request, 'orcamentos/lista_produtos.html', {'produtos': produtos})

def criar_produto(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        preco = request.POST.get('preco')
        
        produto = Produto.objects.create(nome=nome, preco=preco)
        
        # Pega múltiplos arquivos enviados de uma vez
        imagens = request.FILES.getlist('imagens')
        for img in imagens:
            ImagemProduto.objects.create(produto=produto, imagem=img)
            
        return redirect('lista_produtos')
    return render(request, 'orcamentos/form_produto.html')

def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.nome = request.POST.get('nome')
        produto.preco = request.POST.get('preco')
        produto.save()
        
        imagens = request.FILES.getlist('imagens')
        for img in imagens:
            ImagemProduto.objects.create(produto=produto, imagem=img)
            
        return redirect('lista_produtos')
    return render(request, 'orcamentos/form_produto.html', {'produto': produto})

def deletar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        return redirect('lista_produtos')
    return render(request, 'orcamentos/deletar_produto.html', {'produto': produto})

# --- CRUD ORÇAMENTOS ---
def lista_orcamentos(request):
    orcamentos = Orcamento.objects.all()
    return render(request, 'orcamentos/lista_orcamentos.html', {'orcamentos': orcamentos})

def criar_orcamento(request):
    produtos = Produto.objects.all()
    if request.method == 'POST':
        cliente_nome = request.POST.get('cliente_nome')
        produto_id = request.POST.get('produto_id')
        quantidade = request.POST.get('quantidade')
        produto = get_object_or_404(Produto, pk=produto_id)
        Orcamento.objects.create(cliente_nome=cliente_nome, produto=produto, quantidade=quantidade)
        return redirect('lista_orcamentos')
    return render(request, 'orcamentos/form_orcamento.html', {'produtos': produtos})

def detalhe_orcamento(request, pk):
    orcamento = get_object_or_404(Orcamento, pk=pk)
    return render(request, 'orcamentos/detalhe_orcamento.html', {'orcamento': orcamento})

def deletar_orcamento(request, pk):
    orcamento = get_object_or_404(Orcamento, pk=pk)
    if request.method == 'POST':
        orcamento.delete()
        return redirect('lista_orcamentos')
    return render(request, 'orcamentos/deletar_produto.html', {'produto': orcamento})

# --- GERADOR DE PDF COM MÚLTIPLAS IMAGENS CLICÁVEIS ---
def gerar_pdf(request, pk):
    orcamento = get_object_or_404(Orcamento, pk=pk)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Orcamento_{orcamento.id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle(f"Orçamento #{orcamento.id}")

    # Cabeçalho
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(180, 750, "ORÇAMENTO DE VENDA")
    
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 700, f"Cliente: {orcamento.cliente_nome}")
    pdf.drawString(50, 680, f"Data: {orcamento.data.strftime('%d/%m/%Y %H:%M')}")
    pdf.line(50, 665, 550, 665)

    # Dados do Produto
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 640, f"Produto: {orcamento.produto.nome}")
    pdf.drawString(50, 620, f"Quantidade: {orcamento.quantidade}")
    pdf.drawString(50, 600, f"Preço Unitário: R$ {orcamento.produto.preco}")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 575, f"TOTAL GERAL: R$ {orcamento.valor_total()}")
    
    pdf.line(50, 560, 550, 560)

    # Imagens do Produto no PDF
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 540, "Galeria de Fotos do Produto (Clique na imagem para ver em tamanho real):")

    x_pos = 50
    y_pos = 460
    largura = 70
    altura = 70

    imagens = orcamento.produto.imagens.all()
    if imagens.exists():
        for img_obj in imagens:
            if img_obj.imagem and os.path.exists(img_obj.imagem.path):
                try:
                    img = ImageReader(img_obj.imagem.path)
                    pdf.drawImage(img, x_pos, y_pos, width=largura, height=altura, preserveAspectRatio=True)
                    
                    # Torna a imagem clicável no PDF
                    url_completa = request.build_absolute_uri(img_obj.imagem.url)
                    pdf.linkURL(url_completa, (x_pos, y_pos, x_pos + largura, y_pos + altura), relative=1)
                    
                    x_pos += 80 # Espaçamento lateral para a próxima imagem
                    if x_pos > 480: # Pula linha se encher a página
                        x_pos = 50
                        y_pos -= 80
                except Exception:
                    pass
    else:
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, 515, "Nenhuma imagem cadastrada para este produto.")

    pdf.showPage()
    pdf.save()
    
    return response