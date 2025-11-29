import os
from graphviz import Digraph

os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# ============================= ÁRVORE 2-3-4 =============================

class Node234:
    def __init__(self):
        self.keys = []
        self.children = []
        self.parent = None

    def is_leaf(self):
        return len(self.children) == 0

    def is_full(self):
        return len(self.keys) == 3


class Tree234:
    def __init__(self):
        self.root = Node234()

    def search(self, key):
        node = self.root
        while node:
            if key in node.keys:
                return True
            if node.is_leaf():
                return False
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node = node.children[i]
        return False

    def split(self, node):
        parent = node.parent
        mid = node.keys[1]

        left = Node234()
        left.keys = [node.keys[0]]
        left.children = node.children[:2]
        for c in left.children:
            if c: c.parent = left

        right = Node234()
        right.keys = [node.keys[2]]
        right.children = node.children[2:]
        for c in right.children:
            if c: c.parent = right

        # Caso esteja na raiz
        if not parent:
            new_root = Node234()
            new_root.keys = [mid]
            new_root.children = [left, right]
            left.parent = right.parent = new_root
            self.root = new_root
        else:
            i = parent.children.index(node)
            parent.keys.insert(i, mid)
            parent.children[i:i+1] = [left, right]
            left.parent = right.parent = parent

            if parent.is_full():
                self.split(parent)

    def insert(self, key):
        if self.search(key):
            return

        node = self.root
        while not node.is_leaf():
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node = node.children[i]

        # Inserção na folha
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        node.keys.insert(i, key)

        if node.is_full():
            self.split(node)


# ===================== PLOT PASSO A PASSO =====================

def plot_tree234(tree, passo):
    dot = Digraph(comment=f'Árvore 2-3-4 — Passo {passo}')
    dot.attr(rankdir='TB', dpi='250')
    dot.attr('node', shape='box', style='filled,rounded',
             fontname='Arial Bold', fontsize='20', penwidth='3',
             fillcolor='#2e7d32', fontcolor='white')

    def add_node(node):
        if not node.keys:
            return

        label = " | ".join(map(str, node.keys))
        oid = str(id(node))
        dot.node(oid, label)

        for child in node.children:
            if child and child.keys:
                dot.edge(oid, str(id(child)), penwidth='2', color='#1b5e20')
                add_node(child)

    add_node(tree.root)

    nome = f"passo_{passo:02d}"
    dot.render(nome, format="png", cleanup=True)
    print(f"Gerado: {nome}.png")


# ============================= TESTE ============================

print("=== ÁRVORE 2-3-4 ===\n")

t = Tree234()
valores = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45, 55, 65, 75, 85,
           15, 28, 32, 38, 42, 48, 52, 58, 62, 90, 5, 95, 12, 18, 22]

for i, v in enumerate(valores, start=1):
    t.insert(v)
    print(f"Inserido: {v}")
    plot_tree234(t, i)
