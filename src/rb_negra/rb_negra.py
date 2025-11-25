# rb_negra_graphviz_FORÇADO.py
# Funciona mesmo se o PATH estiver zuado

import os
from graphviz import Digraph

# ==================== FORÇA O CAMINHO DO GRAPHVIZ (SOLUÇÃO MÁGICA) ====================
# Mude só se o seu Graphviz foi instalado em outro lugar
GRAPHVIZ_BIN_PATH = r"C:\Program Files\Graphviz\bin"   # 99% dos casos é aqui
os.environ["PATH"] += os.pathsep + GRAPHVIZ_BIN_PATH
# ==================================================================================

class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.parent = None
        self.color = "red"

class RedBlackTree:
    def __init__(self):
        self.NIL = Node(None)
        self.NIL.color = "black"
        self.NIL.left = self.NIL.right = self.NIL
        self.root = self.NIL

    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def right_rotate(self, y):
        x = y.left
        y.left = x.right
        if x.right != self.NIL:
            x.right.parent = y
        x.parent = y.parent
        if y.parent is None:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x

    def insert(self, key):
        if self.search(key):
            return  # ignora duplicados

        node = Node(key)
        node.left = node.right = self.NIL

        y = None
        x = self.root
        while x != self.NIL:
            y = x
            if node.key < x.key:
                x = x.left
            else:
                x = x.right

        node.parent = y
        if y is None:
            self.root = node
        elif node.key < y.key:
            y.left = node
        else:
            y.right = node

        if node.parent is None:
            node.color = "black"
            return
        if node.parent.parent is None:
            return

        self.insert_fix(node)

    def insert_fix(self, k):
        while k.parent and k.parent.color == "red":
            if k.parent == k.parent.parent.right:
                u = k.parent.parent.left
                if u.color == "red":
                    u.color = k.parent.color = "black"
                    k.parent.parent.color = "red"
                    k = k.parent.parent
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self.right_rotate(k)
                    k.parent.color = "black"
                    k.parent.parent.color = "red"
                    self.left_rotate(k.parent.parent)
            else:
                u = k.parent.parent.right
                if u.color == "red":
                    u.color = k.parent.color = "black"
                    k.parent.parent.color = "red"
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self.left_rotate(k)
                    k.parent.color = "black"
                    k.parent.parent.color = "red"
                    self.right_rotate(k.parent.parent)
            if k == self.root:
                break
        self.root.color = "black"

    def search(self, key):
        node = self.root
        while node != self.NIL:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

# ======================== PLOT COM GRAPHVIZ (FORÇADO) ========================
def plot_rubro_negra(tree):
    dot = Digraph(comment='Árvore Rubro-Negra')
    dot.attr(rankdir='TB', size='30,40', dpi='300', bgcolor='white')
    dot.attr('node', shape='circle', style='filled', width='1.3', 
             fontsize='28', fontname='Arial Bold', penwidth='4')

    def add_nodes(node):
        if node == tree.NIL:
            return
        fillcolor = "#e74c3c" if node.color == "red" else "#2c3e50"
        dot.node(str(id(node)), str(node.key), fillcolor=fillcolor, fontcolor="white")

        if node.left != tree.NIL:
            dot.edge(str(id(node)), str(id(node.left)), penwidth='3', color='#2c3e50')
            add_nodes(node.left)
        if node.right != tree.NIL:
            dot.edge(str(id(node)), str(id(node.right)), penwidth='3', color='#2c3e50')
            add_nodes(node.right)

    add_nodes(tree.root)
    nome_arquivo = 'arvore_rubro_negra_PERFEITA'
    dot.render(nome_arquivo, format='png', cleanup=True)
    print(f"\nÁRVORE GERADA COM SUCESSO!")
    print(f"Arquivo salvo como: {nome_arquivo}.png")
    os.startfile(f"{nome_arquivo}.png")  # abre automaticamente no Windows

# ============================= TESTE =============================
rb = RedBlackTree()
print("Inserindo 35 valores na Árvore Rubro-Negra...\n")

valores = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45, 55, 65, 75, 85,
           15, 28, 32, 38, 42, 48, 52, 58, 62, 90, 5, 95, 12, 18, 22, 68, 72, 77, 82, 88]

for v in valores:
    rb.insert(v)
    print(f"Inserido: {v}")

print("\nBusca 42:", rb.search(42))
print("Busca 999:", rb.search(999))

# GERA A IMAGEM PERFEITA
plot_rubro_negra(rb)