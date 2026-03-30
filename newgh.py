import os
import sys
import pandas as pd
import customtkinter as ctk
from tkinter import ttk, messagebox
from PIL import Image
from datetime import datetime


# --- CONFIGURAÇÃO DE DIRETÓRIO ---
def obter_diretorio_app():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


PASTA_APP = obter_diretorio_app()
caminho_excel = os.path.join(PASTA_APP, "alunos.xlsx")
caminho_logo = os.path.join(PASTA_APP, "felipe.ico")


class AppAcademia(ctk.CTk):
    def __init__(self):
        super().__init__()
        # TÍTULO E LAYOUT FIXO
        self.title("GH SYSTEM v12.2 - GESTÃO & PORTFÓLIO (Layout Fixo)")
        self.geometry("1200x850")
        ctk.set_appearance_mode("dark")

        # Tenta colocar o ícone na janela (barra de tarefas)
        if os.path.exists(caminho_logo):
            try:
                self.iconbitmap(caminho_logo)
            except:
                pass

        # Garante que o Excel exista com as colunas certas
        self.configurar_excel_inicial()
        self.df = pd.read_excel(caminho_excel, engine='openpyxl')
        self.abas_tabelas = {}

        # Estas funções PRECISAM estar alinhadas dentro da classe (mesmo nível de espaço)
        self.configurar_interface()
        self.atualizar_todas_tabelas()

    def configurar_excel_inicial(self):
        colunas = ['NOME', 'MODALIDADE', 'IDADE', 'WHATSAPP', 'VENC.', 'STATUS', 'PAR-Q']
        if not os.path.exists(caminho_excel):
            pd.DataFrame(columns=colunas).to_excel(caminho_excel, index=False, engine='openpyxl')
        else:
            # Garante integridade dos dados (ótimo para portfolio de QA)
            df_temp = pd.read_excel(caminho_excel, engine='openpyxl')
            for col in colunas:
                if col not in df_temp.columns:
                    df_temp[col] = "NÃO" if col == "PAR-Q" else "N/A"
            df_temp.to_excel(caminho_excel, index=False, engine='openpyxl')

    # --- FUNÇÃO DE VIRADA DE MÊS (CICLO) ---
    def resetar_mes(self):
        pergunta = messagebox.askyesno("Novo Ciclo Mensal",
                                       "Isso colocará TODOS os alunos como 'Pendente'.\nDeseja iniciar o novo ciclo mensal? (O backup será criado)")
        if pergunta:
            try:
                # Cria backup antes de resetar (ótimo para portfolio de QA)
                data_str = datetime.now().strftime("%Y_%m_%d_%H%M")
                caminho_backup = os.path.join(PASTA_APP, f"backup_alunos_{data_str}.xlsx")
                self.df.to_excel(caminho_backup, index=False)

                # Reseta o status
                self.df['STATUS'] = 'Pendente'
                self.df.to_excel(caminho_excel, index=False, engine='openpyxl')

                self.atualizar_todas_tabelas()
                messagebox.showinfo("Sucesso",
                                    f"Ciclo mensal resetado! Backup salvo como:\nbackup_alunos_{data_str}.xlsx")
            except Exception as e:
                messagebox.showerror("Erro", f"Feche o arquivo Excel antes de resetar!\n{e}")

    def salvar_no_excel(self):
        try:
            nome = self.entry_nome.get().upper().strip()
            if not nome:
                messagebox.showwarning("Atenção", "Nome é obrigatório!")
                return
            novo = pd.DataFrame([{
                'NOME': nome, 'MODALIDADE': self.combo_modalidade.get(),
                'IDADE': self.entry_idade.get(), 'WHATSAPP': self.entry_whatsapp.get(),
                'VENC.': self.entry_venc.get(), 'STATUS': self.combo_status.get(),
                'PAR-Q': "SIM" if self.check_parq.get() else "NÃO"
            }])
            self.df = pd.concat([self.df, novo], ignore_index=True)
            self.df.to_excel(caminho_excel, index=False, engine='openpyxl')

            # Limpar campos
            self.entry_nome.delete(0, 'end')
            self.entry_idade.delete(0, 'end')
            self.check_parq.deselect()

            self.atualizar_todas_tabelas()
            messagebox.showinfo("Sucesso", "Cadastrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")

    def dar_baixa_pagamento(self):
        aba = self.tab_view.get()
        tabela = self.abas_tabelas[aba]["tabela"]
        sel = tabela.selection()
        if not sel: return
        nome = tabela.item(sel)['values'][0]
        self.df.loc[self.df['NOME'] == nome, 'STATUS'] = 'Pago'
        self.df.to_excel(caminho_excel, index=False, engine='openpyxl')
        self.atualizar_todas_tabelas()
        messagebox.showinfo("Sucesso", f"Pagamento de {nome} confirmado!")

    def remover_aluno(self):
        aba = self.tab_view.get()
        tabela = self.abas_tabelas[aba]["tabela"]
        sel = tabela.selection()
        if not sel: return
        nome = tabela.item(sel)['values'][0]
        if messagebox.askyesno("Confirmar", f"Excluir {nome}?"):
            self.df = self.df[self.df['NOME'] != nome]
            self.df.to_excel(caminho_excel, index=False, engine='openpyxl')
            self.atualizar_todas_tabelas()
            messagebox.showinfo("Sucesso", f"Aluno {nome} removido!")

    def filtrar_busca(self, event):
        # Filtra os dados enquanto você digita (Em tempo real)
        self.atualizar_todas_tabelas(self.entry_busca.get().upper())

    def configurar_interface(self):
        # Barra Lateral (fundo escuro fixo)
        self.frame_lat = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#101010")
        self.frame_lat.pack(side="left", fill="y")
        self.frame_lat.pack_propagate(False)

        # LOGO NA LATERAL
        if os.path.exists(caminho_logo):
            try:
                img = ctk.CTkImage(Image.open(caminho_logo), size=(140, 140))
                ctk.CTkLabel(self.frame_lat, image=img, text="").pack(pady=20)
            except:
                ctk.CTkLabel(self.frame_lat, text="GH SYSTEM", font=("Arial", 20, "bold"), text_color="#2b71ed").pack(
                    pady=20)
        else:
            ctk.CTkLabel(self.frame_lat, text="GH SYSTEM", font=("Arial", 20, "bold"), text_color="#2b71ed").pack(
                pady=20)

        # Botões da Lateral
        ctk.CTkButton(self.frame_lat, text="BAIXA PAGAMENTO", fg_color="#10a37f", hover_color="#0d8a6a",
                      command=self.dar_baixa_pagamento).pack(pady=10, padx=20)
        ctk.CTkButton(self.frame_lat, text="REMOVER ALUNO", fg_color="#ef4444", hover_color="#c23535",
                      command=self.remover_aluno).pack(pady=10, padx=20)
        ctk.CTkButton(self.frame_lat, text="INICIAR NOVO MÊS", fg_color="#555555", hover_color="#333333",
                      command=self.resetar_mes).pack(pady=10, padx=20)

        # Área Principal (fundo escuro fixo)
        self.main = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.main.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # Dashboards (Centralizados)
        # Cria um frame invisível só para alinhar os cards no centro
        self.container_cards = ctk.CTkFrame(self.main, fg_color="transparent")
        self.container_cards.pack(pady=10, fill="x")

        self.f_cards = ctk.CTkFrame(self.container_cards, fg_color="transparent")
        self.f_cards.pack(anchor="center")  # Centraliza os cards

        self.val_total = self.criar_card(self.f_cards, "TOTAL ALUNOS", "#2b71ed")
        self.val_atraso = self.criar_card(self.f_cards, "PENDENTES", "#ef4444")

        # Barra de Busca (Em tempo real)
        self.entry_busca = ctk.CTkEntry(self.main, placeholder_text="🔍 Pesquisar aluno por nome...", width=500,
                                        height=35)
        self.entry_busca.pack(pady=10)
        self.entry_busca.bind("<KeyRelease>", self.filtrar_busca)

        # Formulário de Cadastro (Fundo escuro fixo para não dar branco)
        self.f_cad = ctk.CTkFrame(self.main, fg_color="#222222", corner_radius=10)
        self.f_cad.pack(fill="x", pady=5, padx=10)

        self.entry_nome = ctk.CTkEntry(self.f_cad, placeholder_text="Nome Completo", width=250)
        self.entry_nome.grid(row=0, column=0, padx=10, pady=10)
        self.entry_idade = ctk.CTkEntry(self.f_cad, placeholder_text="Idade", width=60)
        self.entry_idade.grid(row=0, column=1, padx=5)
        self.entry_whatsapp = ctk.CTkEntry(self.f_cad, placeholder_text="WhatsApp", width=150)
        self.entry_whatsapp.grid(row=0, column=2, padx=5)
        ctk.CTkButton(self.f_cad, text="CADASTRAR", command=self.salvar_no_excel, width=120, fg_color="#2b71ed").grid(
            row=0, column=3, padx=20)

        self.combo_modalidade = ctk.CTkComboBox(self.f_cad, values=["Jiu-Jitsu", "Judô", "Muay Thai"])
        self.combo_modalidade.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_venc = ctk.CTkEntry(self.f_cad, placeholder_text="Dia Venc.", width=80)
        self.entry_venc.grid(row=1, column=1, sticky="w")
        self.combo_status = ctk.CTkComboBox(self.f_cad, values=["Pago", "Pendente"], width=120)
        self.combo_status.grid(row=1, column=2)
        self.check_parq = ctk.CTkCheckBox(self.f_cad, text="PAR-Q OK")
        self.check_parq.grid(row=1, column=3, padx=10)

        # Abas e Tabelas (Fundo escuro fixo nas tabelas)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1a1a1a", foreground="white", fieldbackground="#1a1a1a", rowheight=28)
        style.configure("Treeview.Heading", background="#2b71ed", foreground="white")
        style.map("Treeview", background=[('selected', '#444444')])

        self.tab_view = ctk.CTkTabview(self.main, fg_color="#1a1a1a")  # Garante fundo escuro na aba
        self.tab_view.pack(expand=True, fill="both", pady=10, padx=10)
        self.configurar_tabelas()

    def criar_card(self, pai, titulo, cor):
        # Card fixo (Fundo escuro)
        f = ctk.CTkFrame(pai, fg_color="#222222", width=180, height=80, border_width=2, border_color=cor)
        f.pack(side="left", padx=15)
        f.pack_propagate(False)  # Trava o tamanho para não "encolher"
        ctk.CTkLabel(f, text=titulo, text_color=cor, font=("Arial", 12, "bold")).pack(pady=5)
        l = ctk.CTkLabel(f, text="0", font=("Arial", 28, "bold"))
        l.pack()
        return l

    def configurar_tabelas(self):
        cols = ("NOME", "IDADE", "WHATSAPP", "VENC.", "STATUS", "PAR-Q")
        mods = ["Geral", "Jiu-Jitsu", "Judô", "Muay Thai"]

        for m in mods:
            aba = self.tab_view.add(m)
            t = ttk.Treeview(aba, columns=cols, show="headings", height=12)
            for c in cols: t.heading(c, text=c); t.column(c, width=100, anchor="center")

            # Tag para colorir pendentes (Vermelho)
            t.tag_configure('atrasado', background="#9e2a2a", foreground="white")
            t.pack(expand=True, fill="both")
            self.abas_tabelas[m] = {"tabela": t, "filtro": None if m == "Geral" else m}

    def atualizar_todas_tabelas(self, busca=""):
        try:
            self.df = pd.read_excel(caminho_excel, engine='openpyxl')
            for mod, info in self.abas_tabelas.items():
                t, f = info["tabela"], info["filtro"]
                # Limpa a tabela antes de preencher
                for i in t.get_children(): t.delete(i)

                dados = self.df if f is None else self.df[self.df['MODALIDADE'] == f]

                # --- APLICA O FILTRO DE BUSCA (se houver) ---
                if busca:
                    dados = dados[dados['NOME'].str.contains(busca, na=False)]

                for _, r in dados.iterrows():
                    # Lógica de cor (Pendente = Vermelho)
                    tag = 'atrasado' if str(r['STATUS']).lower() == 'pendente' else ''
                    t.insert("", "end",
                             values=(r['NOME'], r['IDADE'], r['WHATSAPP'], r['VENC.'], r['STATUS'], r['PAR-Q']),
                             tags=(tag,))

            # Atualiza os Dashboards (Zera os cards para recontar)
            self.val_total.configure(text=str(len(self.df)))
            # No portfolio de QA, mencione que isso é um Dashboard dinâmico
            self.val_atraso.configure(text=str(len(self.df[self.df['STATUS'] == 'Pendente'])))
        except:
            pass


if __name__ == "__main__":
    app = AppAcademia()
    app.mainloop()