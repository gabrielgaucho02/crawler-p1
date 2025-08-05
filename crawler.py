import re
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from openpyxl import Workbook
import threading

DOMINIO_PADRAO = "https://django-anuncios.solyd.com.br"
REGEX_TELEFONE = re.compile(r'(\(?\d{2}\)?\s?\d{4,5}-\d{4})')

# Requisição
def requisicao(url):
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            return resposta.text
    except:
        return ""
    return ""

# Parsing
def parsing(resposta_html):
    try:
        return BeautifulSoup(resposta_html, "html.parser")
    except:
        return None

# Links dos anúncios
def encontrar_links(soup):
    try:
        cards_pai = soup.find("div", class_="ui three doubling link cards")
        return [card.get("href") for card in cards_pai.find_all("a") if card.get("href")]
    except:
        return []

# Telefones
def encontrar_telefones(soup):
    return REGEX_TELEFONE.findall(soup.text)

# Próxima página
def encontrar_proxima_pagina(soup):
    try:
        paginacao = soup.find("a", class_="item", string="Próxima")
        return DOMINIO_PADRAO + paginacao.get("href") if paginacao else None
    except:
        return None

# Salvar em arquivos
def salvar_resultados(telefones):
    caminho_txt = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Arquivo de Texto", "*.txt")])
    if caminho_txt:
        with open(caminho_txt, "w", encoding="utf-8") as arquivo:
            for item in telefones:
                arquivo.write(f"{item}\n")

    caminho_excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Planilha Excel", "*.xlsx")])
    if caminho_excel:
        wb = Workbook()
        ws = wb.active
        ws.title = "Telefones"
        ws.append(["URL", "Telefone"])
        for linha in telefones:
            url, telefone = linha.split(" -> ")
            ws.append([url, telefone])
        wb.save(caminho_excel)

# Função principal
def buscar_telefones():
    btn_buscar.config(state="disabled")
    resultados = []
    url_atual = DOMINIO_PADRAO + "/automoveis/"

    while url_atual:
        html = requisicao(url_atual)
        soup = parsing(html)
        links = encontrar_links(soup)
        for link in links:
            url_completo = DOMINIO_PADRAO + link
            html_anuncio = requisicao(url_completo)
            soup_anuncio = parsing(html_anuncio)
            telefones = encontrar_telefones(soup_anuncio)
            if telefones:
                for tel in telefones:
                    resultados.append(f"{url_completo} -> {tel}")
            else:
                resultados.append(f"{url_completo} -> Telefone não encontrado")
        url_atual = encontrar_proxima_pagina(soup)

    salvar_resultados(resultados)
    messagebox.showinfo("Telefones encontrados", "\n".join(resultados))
    btn_buscar.config(state="normal")

# GUI
janela = tk.Tk()
janela.title("Buscador de Anúncios")

label = tk.Label(janela, text="Clique no botão para buscar telefones.")
label.pack(pady=10)

btn_buscar = tk.Button(janela, text="Buscar Telefones", command=lambda: threading.Thread(target=buscar_telefones).start())
btn_buscar.pack(pady=5)

btn_sair = tk.Button(janela, text="Sair", command=janela.quit)
btn_sair.pack(pady=5)

janela.mainloop()
