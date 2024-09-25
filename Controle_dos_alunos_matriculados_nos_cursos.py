import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox


# Funções para manipulação do banco de dados
def conectar_bd():
    conn = sqlite3.connect('escola.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS alunos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS matriculas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        aluno_id INTEGER NOT NULL,
                        curso_id INTEGER NOT NULL,
                        FOREIGN KEY(aluno_id) REFERENCES alunos(id),
                        FOREIGN KEY(curso_id) REFERENCES cursos(id))''')
    conn.commit()
    return conn


def carregar_alunos():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome FROM alunos')
    alunos = cursor.fetchall()
    for aluno in alunos:
        combobox_alunos['values'] = (*combobox_alunos['values'], aluno[1])
    conn.close()


def carregar_cursos():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome FROM cursos')
    cursos = cursor.fetchall()
    for curso in cursos:
        combobox_cursos['values'] = (*combobox_cursos['values'], curso[1])
    conn.close()


def inserir_matricula(aluno, curso):
    if not aluno or not curso:
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    conn = conectar_bd()
    cursor = conn.cursor()

    # Buscar ID do aluno e do curso selecionados
    cursor.execute('SELECT id FROM alunos WHERE nome = ?', (aluno,))
    aluno_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM cursos WHERE nome = ?', (curso,))
    curso_id = cursor.fetchone()[0]

    cursor.execute('INSERT INTO matriculas (aluno_id, curso_id) VALUES (?, ?)', (aluno_id, curso_id))
    conn.commit()
    conn.close()
    atualizar_treeview()
    limpar_formulario()


def atualizar_treeview():
    for row in tree.get_children():
        tree.delete(row)
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute('''SELECT matriculas.id, alunos.nome, cursos.nome 
                      FROM matriculas 
                      JOIN alunos ON matriculas.aluno_id = alunos.id
                      JOIN cursos ON matriculas.curso_id = cursos.id''')
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)
    conn.close()


def preencher_formulario(event):
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, 'values')
        combobox_alunos.set(valores[1])
        combobox_cursos.set(valores[2])
    except IndexError:
        pass


def alterar_matricula():
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, 'values')
        matricula_id = valores[0]

        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM alunos WHERE nome = ?', (combobox_alunos.get(),))
        aluno_id = cursor.fetchone()[0]
        cursor.execute('SELECT id FROM cursos WHERE nome = ?', (combobox_cursos.get(),))
        curso_id = cursor.fetchone()[0]

        cursor.execute('UPDATE matriculas SET aluno_id = ?, curso_id = ? WHERE id = ?',
                       (aluno_id, curso_id, matricula_id))
        conn.commit()
        conn.close()
        atualizar_treeview()
        limpar_formulario()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione uma matrícula para alterar.")


def excluir_matricula():
    try:
        item_selecionado = tree.selection()[0]
        valores = tree.item(item_selecionado, 'values')
        matricula_id = valores[0]

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM matriculas WHERE id = ?', (matricula_id,))
        conn.commit()
        conn.close()
        atualizar_treeview()
        limpar_formulario()
    except IndexError:
        messagebox.showwarning("Aviso", "Selecione uma matrícula para excluir.")


def limpar_formulario():
    combobox_alunos.set('')
    combobox_cursos.set('')


# Interface gráfica com Tkinter
root = tk.Tk()
root.title("Controle de Alunos Matriculados")

# Campos de formulário
tk.Label(root, text="Aluno").grid(row=0, column=0)
combobox_alunos = ttk.Combobox(root)
combobox_alunos.grid(row=0, column=1)

tk.Label(root, text="Curso").grid(row=1, column=0)
combobox_cursos = ttk.Combobox(root)
combobox_cursos.grid(row=1, column=1)

# TreeView para exibir as matrículas
tree = ttk.Treeview(root, columns=('ID', 'Aluno', 'Curso'), show='headings')
tree.heading('ID', text='ID')
tree.heading('Aluno', text='Aluno')
tree.heading('Curso', text='Curso')
tree.grid(row=3, column=0, columnspan=3)

tree.bind("<ButtonRelease-1>", preencher_formulario)

# Botões
tk.Button(root, text="Incluir", command=lambda: inserir_matricula(combobox_alunos.get(), combobox_cursos.get())).grid(
    row=4, column=0)
tk.Button(root, text="Alterar", command=alterar_matricula).grid(row=4, column=1)
tk.Button(root, text="Excluir", command=excluir_matricula).grid(row=4, column=2)

# Carregar dados iniciais
carregar_alunos()
carregar_cursos()
atualizar_treeview()

root.mainloop()
