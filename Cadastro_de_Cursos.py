import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox


# Funções para manipulação do banco de dados
def conectar_bd():
    conn = sqlite3.connect('escola.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cursos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        duracao INTEGER NOT NULL)''')
    conn.commit()
    return conn


def inserir_curso(nome, duracao):
    if not nome or not duracao:
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO cursos (nome, duracao) VALUES (?, ?)', (nome, duracao))
    conn.commit()
    conn.close()
    atualizar_treeview()
    limpar_formulario()


def atualizar_treeview():
    for row in tree.get_children():
        tree.delete(row)
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cursos')
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)
    conn.close()


def preencher_formulario(event):
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, 'values')
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, valores[1])
        entry_duracao.delete(0, tk.END)
        entry_duracao.insert(0, valores[2])
    except IndexError:
        pass


def alterar_curso():
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, 'values')
        curso_id = valores[0]

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('UPDATE cursos SET nome = ?, duracao = ? WHERE id = ?',
                       (entry_nome.get(), entry_duracao.get(), curso_id))
        conn.commit()
        conn.close()
        atualizar_treeview()
        limpar_formulario()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione um curso para alterar.")


def excluir_curso():
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, 'values')
        curso_id = valores[0]

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cursos WHERE id = ?', (curso_id,))
        conn.commit()
        conn.close()
        atualizar_treeview()
        limpar_formulario()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione um curso para excluir.")


def limpar_formulario():
    entry_nome.delete(0, tk.END)
    entry_duracao.delete(0, tk.END)


# Interface gráfica com Tkinter
root = tk.Tk()
root.title("Cadastro de Cursos")

# Campos de formulário
tk.Label(root, text="Nome do Curso").grid(row=0, column=0)
entry_nome = tk.Entry(root)
entry_nome.grid(row=0, column=1)

tk.Label(root, text="Duração (meses)").grid(row=1, column=0)
entry_duracao = tk.Entry(root)
entry_duracao.grid(row=1, column=1)

# TreeView para exibir os cursos
tree = ttk.Treeview(root, columns=('ID', 'Nome', 'Duração'), show='headings')
tree.heading('ID', text='ID')
tree.heading('Nome', text='Nome')
tree.heading('Duração', text='Duração (meses)')
tree.grid(row=3, column=0, columnspan=3)

tree.bind("<ButtonRelease-1>", preencher_formulario)

# Botões
tk.Button(root, text="Incluir", command=lambda: inserir_curso(entry_nome.get(), entry_duracao.get())).grid(row=4,
                                                                                                           column=0)
tk.Button(root, text="Alterar", command=alterar_curso).grid(row=4, column=1)
tk.Button(root, text="Excluir", command=excluir_curso).grid(row=4, column=2)

# Atualizar a lista de cursos
atualizar_treeview()

root.mainloop()
