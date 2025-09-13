import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3


def criar_tabela():
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS livros (
          id INTEGER PRIMARY KEY,
          titulo TEXT NOT NULL,
          autor TEXT NOT NULL,
          ano INTEGER NOT NULL,
          disponivel BOOLEAN NOT NULL
      )
    """)
    conn.commit()
    conn.close()


def adicionar_livros(titulo, autor, ano, disponivel):
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO livros (titulo, autor, ano, disponivel) VALUES (?, ?, ?, ?)',
                   (titulo, autor, ano, disponivel))
    conn.commit()
    conn.close()


def listar_livros():
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    conn.close()
    return livros


def atualizar_livro(id, titulo, autor, ano, disponivel):
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE livros SET titulo = ?, autor = ?, ano = ?, disponivel = ? WHERE id = ?',
                   (titulo, autor, ano, disponivel, id))
    conn.commit()
    conn.close()


def deletar_livro(id):
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM livros WHERE id = ?', (id,))
    conn.commit()
    conn.close()


class BibliotecaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Biblioteca CRUD")

        # Frame para formulário
        form_frame = tk.Frame(root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Título").grid(row=0, column=0)
        self.titulo_var = tk.StringVar()
        self.titulo_entry = tk.Entry(form_frame, textvariable=self.titulo_var)
        self.titulo_entry.grid(row=0, column=1)

        tk.Label(form_frame, text="Autor").grid(row=1, column=0)
        self.autor_var = tk.StringVar()
        self.autor_entry = tk.Entry(form_frame, textvariable=self.autor_var)
        self.autor_entry.grid(row=1, column=1)

        tk.Label(form_frame, text="Ano").grid(row=2, column=0)
        self.ano_var = tk.StringVar()
        self.ano_entry = tk.Entry(form_frame, textvariable=self.ano_var)
        self.ano_entry.grid(row=2, column=1)


        tk.Label(form_frame, text="Disponível").grid(row=3, column=0)
        self.disponivel_var = tk.BooleanVar()
        self.disponivel_check = tk.Checkbutton(form_frame, variable=self.disponivel_var)
        self.disponivel_check.grid(row=3, column=1)

        # Botões para ações
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.add_btn = tk.Button(btn_frame, text="Adicionar", command=self.adicionar)
        self.add_btn.grid(row=0, column=0, padx=5)

        self.update_btn = tk.Button(btn_frame, text="Atualizar", command=self.atualizar)
        self.update_btn.grid(row=0, column=1, padx=5)

        self.delete_btn = tk.Button(btn_frame, text="Deletar", command=self.deletar)
        self.delete_btn.grid(row=0, column=2, padx=5)

        self.clear_btn = tk.Button(btn_frame, text="Limpar Campos", command=self.limpar_campos)
        self.clear_btn.grid(row=0, column=3, padx=5)

        # Treeview para listar os livros
        self.tree = ttk.Treeview(root, columns=("ID", "Título", "Autor", "Ano", "Disponível"), show='headings')
        self.tree.pack()
        for col in ("ID", "Título", "Autor", "Ano", "Disponível"):
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=0, width=100)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        self.carregar_livros()

    def carregar_livros(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for livro in listar_livros():
            disp = "Sim" if livro[4] else "Não"
            self.tree.insert("", "end", values=(livro[0], livro[1], livro[2], livro[3], disp))

    def adicionar(self):
        try:
            titulo = self.titulo_var.get()
            autor = self.autor_var.get()
            ano = int(self.ano_var.get())
            disponivel = self.disponivel_var.get()
            if not titulo or not autor:
                messagebox.showwarning("AVISO", "Título e Autor são obrigatórios.")
                return
            adicionar_livros(titulo, autor, ano, disponivel)
            self.carregar_livros()
            self.limpar_campos()
            messagebox.showinfo("SUCESSO", "Livro adicionado com sucesso!")
        except ValueError:
            messagebox.showerror("ERRO", "Ano deve ser um número inteiro.")

    def atualizar(self):
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("AVISO", "Selecione um livro para atualizar.")
                return
            id = self.tree.item(selected[0])['values'][0]
            titulo = self.titulo_var.get()
            autor = self.autor_var.get()
            ano = int(self.ano_var.get())
            disponivel = self.disponivel_var.get()
            if not titulo or not autor:
                messagebox.showwarning("AVISO", "Título e Autor são obrigatórios.")
                return
            atualizar_livro(id, titulo, autor, ano, disponivel)
            self.carregar_livros()
            self.limpar_campos()
            messagebox.showinfo("SUCESSO", "Livro atualizado com sucesso!")
        except ValueError:
            messagebox.showerror("ERRO", "Ano deve ser um número inteiro.")

    def deletar(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("AVISO", "Selecione um livro para deletar.")
            return
        id = self.tree.item(selected[0])['values'][0]
        deletar_livro(id)
        self.carregar_livros()
        self.limpar_campos()
        messagebox.showinfo("SUCESSO", "Livro deletado com sucesso!")

    def limpar_campos(self):
        self.titulo_var.set("")
        self.autor_var.set("")
        self.ano_var.set("")
        self.disponivel_var.set(False)
        self.tree.selection_remove(self.tree.selection())

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            self.titulo_var.set(item['values'][1])
            self.autor_var.set(item['values'][2])
            self.ano_var.set(item['values'][3])
            self.disponivel_var.set(item['values'][4] == "Sim")


if __name__ == "__main__":
    criar_tabela()
    root = tk.Tk()
    app = BibliotecaApp(root)
    root.mainloop()