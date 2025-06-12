from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from tkinter import messagebox, filedialog, simpledialog
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from selenium.webdriver.common.keys import Keys
import xml.etree.ElementTree as ET
import os
import time

# Arquivos XML
CONTATOS_FILE = "contatos.xml"
MENSAGENS_FILE = "mensagens.xml"

# ========== GERENCIAMENTO DE CONTATOS ==========
def carregar_contatos():
    if not os.path.exists(CONTATOS_FILE):
        root = ET.Element("Contatos")
        tree = ET.ElementTree(root)
        tree.write(CONTATOS_FILE)
        return []
    
    tree = ET.parse(CONTATOS_FILE)
    return [{
        'nome': c.find('Nome').text,
        'empresa': c.find('Empresa').text,
        'numero': c.find('Numero').text
    } for c in tree.findall('Contato')]

def salvar_contatos(contatos):
    root = ET.Element("Contatos")
    for c in contatos:
        contato = ET.SubElement(root, "Contato")
        ET.SubElement(contato, "Nome").text = c['nome']
        ET.SubElement(contato, "Empresa").text = c['empresa']
        ET.SubElement(contato, "Numero").text = c['numero']
    ET.ElementTree(root).write(CONTATOS_FILE)

# ========== GERENCIAMENTO DE MENSAGENS ==========
def carregar_mensagens():
    if not os.path.exists(MENSAGENS_FILE):
        root = ET.Element("Mensagens")
        tree = ET.ElementTree(root)
        tree.write(MENSAGENS_FILE)
        return []
    
    tree = ET.parse(MENSAGENS_FILE)
    return [{
        'titulo': m.find('Titulo').text,
        'texto': m.find('Texto').text
    } for m in tree.findall('Mensagem')]

def salvar_mensagens(mensagens):
    root = ET.Element("Mensagens")
    for m in mensagens:
        mensagem = ET.SubElement(root, "Mensagem")
        ET.SubElement(mensagem, "Titulo").text = m['titulo']
        ET.SubElement(mensagem, "Texto").text = m['texto']
    ET.ElementTree(root).write(MENSAGENS_FILE)

# ========== FUNÇÕES DE INTERFACE ==========
def adicionar_item(tipo, listbox, carregar_fn, salvar_fn):
    if tipo == "contato":
        nome = simpledialog.askstring("Novo Contato", "Nome da Pessoa:")
        if not nome: return
        empresa = simpledialog.askstring("Novo Contato", "Nome da Empresa:")
        numero = simpledialog.askstring("Novo Contato", "Número (com DDD):")
        if nome and numero:
            novo_item = {'nome': nome, 'empresa': empresa or "", 'numero': numero}
    else:
        titulo = simpledialog.askstring("Nova Mensagem", "Título da Mensagem:")
        if not titulo: return
        texto = simpledialog.askstring("Nova Mensagem", "Texto da Mensagem:")
        if titulo and texto:
            novo_item = {'titulo': titulo, 'texto': texto}
    
    itens = carregar_fn()
    itens.append(novo_item)
    salvar_fn(itens)
    atualizar_lista(listbox, carregar_fn)

def editar_item(tipo, listbox, carregar_fn, salvar_fn):
    selecionado = listbox.curselection()
    if not selecionado: return
    
    itens = carregar_fn()
    item = itens[selecionado[0]]
    
    if tipo == "contato":
        nome = simpledialog.askstring("Editar Contato", "Nome:", initialvalue=item['nome'])
        empresa = simpledialog.askstring("Editar Contato", "Empresa:", initialvalue=item['empresa'])
        numero = simpledialog.askstring("Editar Contato", "Número:", initialvalue=item['numero'])
        if nome and numero:
            itens[selecionado[0]] = {'nome': nome, 'empresa': empresa or "", 'numero': numero}
    else:
        titulo = simpledialog.askstring("Editar Mensagem", "Título:", initialvalue=item['titulo'])
        texto = simpledialog.askstring("Editar Mensagem", "Texto:", initialvalue=item['texto'])
        if titulo and texto:
            itens[selecionado[0]] = {'titulo': titulo, 'texto': texto}
    
    salvar_fn(itens)
    atualizar_lista(listbox, carregar_fn)

def remover_item(listbox, carregar_fn, salvar_fn):
    selecionado = listbox.curselection()
    if not selecionado: return
    
    if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este item?"):
        itens = carregar_fn()
        del itens[selecionado[0]]
        salvar_fn(itens)
        atualizar_lista(listbox, carregar_fn)

def atualizar_lista(listbox, carregar_fn):
    listbox.delete(0, END)
    for item in carregar_fn():
        if 'numero' in item:  # É um contato
            listbox.insert(END, f"{item['nome']} | {item['empresa']} | {item['numero']}")
        else:  # É uma mensagem
            listbox.insert(END, f"{item['titulo']}")

def obter_selecionados(listbox, carregar_fn):
    selecionados = listbox.curselection()
    itens = carregar_fn()
    return [itens[i] for i in selecionados]

def inserir_mensagem_selecionada(event, listbox_mensagens, text_widget):
    selecionados = obter_selecionados(listbox_mensagens, carregar_mensagens)
    if selecionados:
        text_widget.delete("1.0", END)
        text_widget.insert("1.0", selecionados[0]['texto'])

# ========== INTERFACE PRINCIPAL ==========
def interface():
    root = tk.Tk()
    root.title("WhatsApp Sender Pro")
    
    notebook = ttk.Notebook(root)
    notebook.pack(padx=10, pady=10, fill=BOTH, expand=True)
    
    # Aba Contatos
    frame_contatos = ttk.Frame(notebook)
    notebook.add(frame_contatos, text="Gerenciar Contatos")
    
    listbox_contatos = Listbox(frame_contatos, width=80, height=15, selectmode=MULTIPLE)
    scroll_contatos = Scrollbar(frame_contatos, command=listbox_contatos.yview)
    listbox_contatos.config(yscrollcommand=scroll_contatos.set)
    
    scroll_contatos.pack(side=RIGHT, fill=Y)
    listbox_contatos.pack(pady=10, fill=BOTH, expand=True)
    
    btn_frame_contatos = ttk.Frame(frame_contatos)
    btn_frame_contatos.pack(fill=X)
    
    ttk.Button(btn_frame_contatos, text="Adicionar",
              command=lambda: adicionar_item("contato", listbox_contatos, carregar_contatos, salvar_contatos)).pack(side=LEFT, padx=5)
    ttk.Button(btn_frame_contatos, text="Editar",
              command=lambda: editar_item("contato", listbox_contatos, carregar_contatos, salvar_contatos)).pack(side=LEFT, padx=5)
    ttk.Button(btn_frame_contatos, text="Remover",
              command=lambda: remover_item(listbox_contatos, carregar_contatos, salvar_contatos)).pack(side=LEFT, padx=5)
    
    # Aba Mensagens
    frame_mensagens = ttk.Frame(notebook)
    notebook.add(frame_mensagens, text="Gerenciar Mensagens")
    
    listbox_mensagens = Listbox(frame_mensagens, width=80, height=15)
    scroll_mensagens = Scrollbar(frame_mensagens, command=listbox_mensagens.yview)
    listbox_mensagens.config(yscrollcommand=scroll_mensagens.set)
    
    scroll_mensagens.pack(side=RIGHT, fill=Y)
    listbox_mensagens.pack(pady=10, fill=BOTH, expand=True)
    
    btn_frame_mensagens = ttk.Frame(frame_mensagens)
    btn_frame_mensagens.pack(fill=X)
    
    ttk.Button(btn_frame_mensagens, text="Adicionar",
              command=lambda: adicionar_item("mensagem", listbox_mensagens, carregar_mensagens, salvar_mensagens)).pack(side=LEFT, padx=5)
    ttk.Button(btn_frame_mensagens, text="Editar",
              command=lambda: editar_item("mensagem", listbox_mensagens, carregar_mensagens, salvar_mensagens)).pack(side=LEFT, padx=5)
    ttk.Button(btn_frame_mensagens, text="Remover",
              command=lambda: remover_item(listbox_mensagens, carregar_mensagens, salvar_mensagens)).pack(side=LEFT, padx=5)
    
    # Aba Envio
    frame_envio = ttk.Frame(notebook)
    notebook.add(frame_envio, text="Enviar Mensagens")
    
    # Seleção de Mensagem
    ttk.Label(frame_envio, text="Mensagens Pré-definidas:").pack(anchor=W)
    listbox_msg_envio = Listbox(frame_envio, height=5)
    scroll_msg = Scrollbar(frame_envio, command=listbox_msg_envio.yview)
    listbox_msg_envio.config(yscrollcommand=scroll_msg.set)
    
    scroll_msg.pack(side=RIGHT, fill=Y)
    listbox_msg_envio.pack(fill=X, pady=5)
    listbox_msg_envio.bind("<Double-Button-1>", lambda e: inserir_mensagem_selecionada(e, listbox_msg_envio, mensagem_text))
    
    # Editor de Mensagem
    ttk.Label(frame_envio, text="Mensagem:").pack(anchor=W)
    mensagem_text = Text(frame_envio, height=10)
    mensagem_text.pack(fill=BOTH, expand=True, pady=5)
    
    # Botão Enviar
    ttk.Button(frame_envio, text="ENVIAR PARA CONTATOS SELECIONADOS", 
              command=lambda: enviar_mensagens(
                  [c['numero'] for c in obter_selecionados(listbox_contatos, carregar_contatos)],
                  mensagem_text.get("1.0", END)
              )).pack(pady=10)
    
    # Carrega dados iniciais
    atualizar_lista(listbox_contatos, carregar_contatos)
    atualizar_lista(listbox_mensagens, carregar_mensagens)
    atualizar_lista(listbox_msg_envio, carregar_mensagens)
    
    root.mainloop()

# ========== FUNÇÕES DE ENVIO ==========
def enviar_mensagens(contatos, mensagem):
    if not contatos:
        messagebox.showerror('Erro', 'Nenhum contato selecionado!')
        return
    
    if not messagebox.askyesno('Confirmar', f'Enviar para {len(contatos)} contatos?'):
        return
    
    servico = Service(ChromeDriverManager().install())
    navegador = webdriver.Chrome(service=servico)
    navegador.get("https://web.whatsapp.com/")
    messagebox.showwarning('CONECTAR', 'LEIA O QR CODE E AGUARDE O CARREGAMENTO')
    
    try:
        WebDriverWait(navegador, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
        )
        
        for contato in contatos:
            try:
                search = navegador.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                search.clear()
                search.send_keys(contato)
                time.sleep(2)
                
                contato_element = navegador.find_element(By.XPATH, f'//span[@title="{contato}"]')
                contato_element.click()
                time.sleep(1)
                
                if arquivo:
                    navegador.find_element(By.XPATH, '//div[@title="Anexar"]').click()
                    time.sleep(1)
                    navegador.find_element(By.XPATH, '//input[@accept="*"]').send_keys(os.path.abspath(arquivo))
                    time.sleep(3)
                
                msg_box = navegador.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                msg_box.send_keys(mensagem + Keys.ENTER)
                time.sleep(2)
                
            except Exception as e:
                messagebox.showerror('Erro', f'Falha ao enviar para {contato}')
                continue
    
    finally:
        navegador.quit()
        messagebox.showinfo('Concluído', 'Processo finalizado!')

if __name__ == "__main__":
    interface()
