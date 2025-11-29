import os
import copy
from graphviz import Digraph
import imageio
from datetime import datetime
from typing import Optional

# GRAPHVIZ_BIN_PATH = r"C:\Program Files\Graphviz\bin"
# os.environ["PATH"] += os.pathsep + GRAPHVIZ_BIN_PATH

class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.parent = None
        self.color = "red"

    def __repr__(self):
        return f"Node({self.key},{self.color})"

class RedBlackTree:
    def __init__(self):
        # sentinel NIL único da árvore "viva"
        self.NIL = Node(None)
        self.NIL.color = "black"
        self.NIL.left = self.NIL.right = self.NIL
        self.root = self.NIL

        # registro de snapshots — cada entry tem: idx, ts, descricao, root_copy
        self._steps = []
        self._step_counter = 0
        # snapshot do estado inicial (árvore vazia)
        self._snapshot("inicial (vazia)")

    def _snapshot(self, descricao: str) -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        # copia profunda da árvore, criando novos nós e novo sentinel
        copia_root = self._copy_tree(self.root)
        entry = {"idx": self._step_counter, "ts": ts, "descricao": descricao, "root": copia_root}
        self._steps.append(entry)
        self._step_counter += 1

    def _copy_tree(self, node, parent=None):
        if node is None:
            return None
        if node == self.NIL or node.key is None:
            nil_new = Node(None)
            nil_new.color = "black"
            nil_new.left = nil_new.right = nil_new
            return nil_new

        new_node = Node(node.key)
        new_node.color = node.color
        new_node.parent = parent

        new_node.left = self._copy_tree(node.left, new_node)
        new_node.right = self._copy_tree(node.right, new_node)

        return new_node

    # ---------------- Export ----------------
    def export_steps(self, out_dir: str = "arvore_steps", png: bool = True, gif: bool = False, gif_name: str = "arvore_evolucao.gif", open_after: bool = False) -> None:
        os.makedirs(out_dir, exist_ok=True)
        png_files = []
        for step in self._steps:
            idx = step["idx"]
            desc = step["descricao"]
            root_copy = step["root"]  # cópia do estado naquele passo
            filename_base = f"step_{idx:03d}_{self._sanitize(desc)}"
            png_path = os.path.join(out_dir, filename_base + ".png")
            self._render_png(root_copy, png_path, title=f"{idx:03d} - {desc}")
            png_files.append(png_path)

        if gif:
            frames = []
            for p in png_files:
                frames.append(imageio.imread(p))
            gif_path = os.path.join(out_dir, gif_name)
            imageio.mimsave(gif_path, frames, duration=0.8)
            print(f"GIF salvo em: {gif_path}")
            if open_after:
                try:
                    os.startfile(gif_path)
                except Exception:
                    pass

        if png:
            print(f"PNG(s) salvos em: {os.path.abspath(out_dir)}")
            if open_after and png_files:
                try:
                    os.startfile(png_files[-1])
                except Exception:
                    pass

    def _sanitize(self, text: str) -> str:
        ok = "".join(ch if (ch.isalnum() or ch in "-_") else "_" for ch in text)
        return (ok[:60]).strip("_")

    def _node_id(self, node):
        return f"n{str(id(node))}"

    def _render_png(self, root_node, out_path: str, title: Optional[str] = None) -> None:
        dot = Digraph(comment=title or "RubroNegra")
        dot.attr(rankdir='TB')
        dot.attr('node', shape='circle', style='filled', fontsize='12', fontname='Arial')

        def add_nodes(n):
            if n is None:
                return
            if getattr(n, "key", None) is None:
                return
            fillcolor = "#e74c3c" if n.color == "red" else "#2c3e50"
            label = str(n.key)
            dot.node(self._node_id(n), label, fillcolor=fillcolor, fontcolor="white", penwidth='1.2')
            if getattr(n.left, "key", None) is not None:
                dot.edge(self._node_id(n), self._node_id(n.left))
                add_nodes(n.left)
            if getattr(n.right, "key", None) is not None:
                dot.edge(self._node_id(n), self._node_id(n.right))
                add_nodes(n.right)

        if root_node is None or getattr(root_node, "key", None) is None:
            dot.node("root_nil", "Árvore Vazia", fillcolor="#bdc3c7")
        else:
            add_nodes(root_node)

        out_path_base, _ = os.path.splitext(out_path)
        dot.render(out_path_base, format='png', cleanup=True)

    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if getattr(y.left, "key", None) is not None:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None or getattr(x.parent, "key", None) is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        self._snapshot(f"left_rotate em {x.key}")

    def right_rotate(self, y):
        x = y.left
        y.left = x.right
        if getattr(x.right, "key", None) is not None:
            x.right.parent = y
        x.parent = y.parent
        if y.parent is None or getattr(y.parent, "key", None) is None:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x
        self._snapshot(f"right_rotate em {y.key}")

    # ---------------- Insert ----------------
    def insert(self, key):
        if self.search(key):
            # evita duplicados
            self._snapshot(f"insercao_ignorada ({key}) - duplicado")
            return

        node = Node(key)
        node.left = node.right = self.NIL

        y = None
        x = self.root
        while x != self.NIL and getattr(x, "key", None) is not None:
            y = x
            if node.key < x.key:
                x = x.left
            else:
                x = x.right

        node.parent = y
        if y is None or getattr(y, "key", None) is None:
            self.root = node
        elif node.key < y.key:
            y.left = node
        else:
            y.right = node

        # snapshot logo após posicionar o nó (antes do fix)
        self._snapshot(f"insercao ({key}) - posicionado")

        if node.parent is None or getattr(node.parent, "key", None) is None:
            node.color = "black"
            self._snapshot(f"insercao ({key}) - tornou-se raiz (preto)")
            return
        if node.parent.parent is None or getattr(node.parent.parent, "key", None) is None:
            # pai não tem avô — geralmente sem fix necessário
            self._snapshot(f"insercao ({key}) - pai sem avô (sem fix)")
            return

        self.insert_fix(node)
        # snapshot final da inserção
        self._snapshot(f"insercao ({key}) - finalizada")

    def insert_fix(self, k):
        while k.parent and getattr(k.parent, "color", None) == "red":
            if k.parent == k.parent.parent.right:
                u = k.parent.parent.left
                if getattr(u, "color", None) == "red":
                    #! recoloração (caso 1)
                    u.color = k.parent.color = "black"
                    k.parent.parent.color = "red"
                    self._snapshot(f"recoloracao (caso 1) em avô {k.parent.parent.key}")
                    k = k.parent.parent
                else:
                    #! rotacoes e recoloracoes (caso 2/3)
                    if k == k.parent.left:
                        k = k.parent
                        self.right_rotate(k)
                    k.parent.color = "black"
                    k.parent.parent.color = "red"
                    self.left_rotate(k.parent.parent)
                    self._snapshot(f"rotacao+recoloracao em avô {k.parent.key if k.parent else 'desconhecido'}")
            else:
                u = k.parent.parent.right
                if getattr(u, "color", None) == "red":
                    u.color = k.parent.color = "black"
                    k.parent.parent.color = "red"
                    self._snapshot(f"recoloracao (caso 1) em avô {k.parent.parent.key}")
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self.left_rotate(k)
                    k.parent.color = "black"
                    k.parent.parent.color = "red"
                    self.right_rotate(k.parent.parent)
                    self._snapshot(f"rotacao+recoloracao em avô {k.parent.key if k.parent else 'desconhecido'}")
            if k == self.root:
                break
        if self.root != self.NIL:
            self.root.color = "black"
        self._snapshot("root colorida de preto (final do insert_fix)")

    #* ---------------- Search ----------------
    def search(self, key):
        node = self.root
        while node != self.NIL and getattr(node, "key", None) is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

if __name__ == "__main__":
    rb = RedBlackTree()

    valores = [30, 15, 10, 40, 20, 35, 50, 5, 12, 18, 25, 32, 37, 45, 55, 3, 8, 11, 14, 17, 19]

    print(f"Inserindo {len(valores)} nós: {valores}")
    for v in valores:
        rb.insert(v)
        print(f"  -> inserido {v}")

    rb.export_steps(out_dir="arvore_steps", png=True, gif=False, gif_name="construcao_rbt.gif", open_after=False)
    print("Export concluído.")
