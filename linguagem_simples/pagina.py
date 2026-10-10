"""Texto de uma página HTML, com a posição de cada caractere no arquivo.

O texto sai em blocos como no Markdown (linha em branco entre blocos, "- "
no item de lista, "# " no título), para os detectores lerem do mesmo jeito.
Cada caractere guarda onde começa e onde acaba no HTML: o relatório dá a
linha e a coluna no arquivo lido, não no texto extraído. Links, imagens e
tabelas vêm à parte, em ``elementos``, para o inciso XVII.
"""

import re
from bisect import bisect_left
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser

# Conteúdo que não é texto corrido da página: código, metadados, menu e
# campos de formulário.
_FORA = frozenset({
    "head", "script", "style", "noscript", "template", "svg", "math", "nav",
    "iframe", "object", "select", "textarea",
})
_BLOCO = frozenset({
    "address", "article", "aside", "blockquote", "caption", "dd", "details",
    "dialog", "div", "dl", "dt", "fieldset", "figcaption", "figure", "footer",
    "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "legend", "li",
    "main", "ol", "p", "pre", "section", "summary", "table", "tbody", "td",
    "tfoot", "th", "thead", "tr", "ul",
})
_MARCA = {"li": "- ", "h1": "# ", "h2": "# ", "h3": "# ", "h4": "# ", "h5": "# ", "h6": "# "}
_VAZIO = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
})
_CHARSET = re.compile(rb"<meta[^>]+charset\s*=\s*[\"']?([\w-]+)", re.IGNORECASE)
_PARECE_HTML = re.compile(rb"(?:\xef\xbb\xbf)?\s*<(?:!doctype\s+html|html)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Elemento:
    """Link (``a`` com ``href``), imagem ou tabela da página."""
    tag: str          # "a", "img" ou "table"
    inicio: int       # no HTML, do "<" da abertura
    fim: int          # até o fim do fechamento; na imagem, o fim da própria tag
    atributos: tuple  # pares (nome, valor) da abertura, como o HTMLParser dá
    texto: str = ""   # link: o texto dentro dele, com o alt das imagens
    cabecalho: bool = False  # tabela: tem célula ``th``

    def atributo(self, nome):
        """Valor do atributo (``""`` se vier sem valor) ou ``None``."""
        for n, v in self.atributos:
            if n == nome:
                return v or ""
        return None


@dataclass(frozen=True)
class Pagina:
    fonte: str     # o HTML lido
    texto: str     # o texto extraído, em blocos
    inicios: tuple  # posição no HTML onde começa cada caractere do texto
    fins: tuple     # e onde acaba
    elementos: tuple = ()  # links, imagens e tabelas, na ordem do HTML

    def na_fonte(self, inicio, fim):
        """Início e fim no HTML do trecho ``texto[inicio:fim]``."""
        if fim <= inicio:
            a = self.inicios[inicio] if inicio < len(self.inicios) else len(self.fonte)
            return a, a
        return self.inicios[inicio], self.fins[fim - 1]

    def no_texto(self, inicio, fim):
        """Início e fim no texto do trecho ``fonte[inicio:fim]`` do HTML."""
        return bisect_left(self.inicios, inicio), bisect_left(self.inicios, fim)


def parece_html(dados):
    """Bytes que começam por ``<!doctype html`` ou ``<html``."""
    return bool(_PARECE_HTML.match(dados))


def decodificar(dados):
    """HTML em bytes para texto: UTF-8 ou, se não for, o charset que a
    página declara. Sem charset declarado, o erro de UTF-8 sobe."""
    try:
        return dados.decode("utf-8-sig")
    except UnicodeDecodeError:
        m = _CHARSET.search(dados[:4096])
        if not m:
            raise
        return dados.decode(m.group(1).decode("ascii"))


def ler_html(fonte):
    """Uma ``Pagina`` com o texto do HTML. Se houver ``<main>``, só o que
    está dentro dele; sem ``<main>``, a página inteira, menos o que está em
    ``_FORA`` e o que tem o atributo ``hidden``."""
    leitor = _Leitor(fonte)
    leitor.feed(fonte)
    leitor.close()
    pedacos, elementos = leitor.pedacos, leitor.elementos
    if leitor.tem_main:
        pedacos = [p for p in pedacos if p[4]]
        elementos = [e for e in elementos if e[1]]
    elementos = tuple(sorted((e for e, _ in elementos), key=lambda e: e.inicio))
    return _montar(fonte, pedacos, elementos)


class _Leitor(HTMLParser):
    def __init__(self, fonte):
        super().__init__(convert_charrefs=False)
        self.inicio_da_linha = [0] + [m.end() for m in re.finditer("\n", fonte)]
        self.fonte = fonte
        self.pedacos = []  # (tipo, texto, inicio, fim, dentro do main)
        self.fora = []     # elementos abertos dentro de um trecho que não conta
        self.main = 0
        self.tem_main = False
        self.elementos = []  # (Elemento, dentro do main)
        self.links = []      # abertos: [inicio, atributos, partes do texto, dentro do main]
        self.tabelas = []    # abertas: [inicio, atributos, tem th, dentro do main]

    def _pos(self):
        linha, coluna = self.getpos()
        return self.inicio_da_linha[linha - 1] + coluna

    def _guardar(self, tipo, texto, inicio, fim):
        if not self.fora:
            self.pedacos.append((tipo, texto, inicio, fim, self.main > 0))
            if self.links and tipo in ("texto", "entidade"):
                self.links[-1][2].append(texto)

    def handle_starttag(self, tag, attrs):
        if self.fora or tag in _FORA or any(nome == "hidden" for nome, _ in attrs):
            if tag not in _VAZIO:
                self.fora.append(tag)
            return
        inicio = self._pos()
        fim = inicio + len(self.get_starttag_text())
        if tag == "main":
            self.main += 1
            self.tem_main = True
        if tag == "br":
            self._guardar("linha", "", inicio, fim)
        elif tag in _BLOCO:
            self._guardar("bloco", _MARCA.get(tag, ""), inicio, fim)
        dentro = self.main > 0
        if tag == "a" and any(nome == "href" for nome, _ in attrs):
            self.links.append([inicio, attrs, [], dentro])
        elif tag == "img":
            alt = dict(attrs).get("alt")
            if self.links and alt:
                self.links[-1][2].append(alt)
            self.elementos.append((Elemento("img", inicio, fim, tuple(attrs)), dentro))
        elif tag == "table":
            self.tabelas.append([inicio, attrs, False, dentro])
        elif tag == "th" and self.tabelas:
            self.tabelas[-1][2] = True

    def handle_endtag(self, tag):
        if self.fora:
            if tag in self.fora:
                del self.fora[len(self.fora) - 1 - self.fora[::-1].index(tag):]
            return
        if tag in _BLOCO:
            inicio = self._pos()
            self._guardar("bloco", "", inicio, inicio)
        if tag == "a" and self.links or tag == "table" and self.tabelas:
            fim = self.fonte.find(">", self._pos()) + 1 or len(self.fonte)
            if tag == "a":
                inicio, attrs, partes, dentro = self.links.pop()
                texto = " ".join(" ".join(partes).split())
                self.elementos.append((Elemento("a", inicio, fim, tuple(attrs), texto), dentro))
            else:
                inicio, attrs, th, dentro = self.tabelas.pop()
                self.elementos.append((Elemento("table", inicio, fim, tuple(attrs), cabecalho=th), dentro))
        if tag == "main" and self.main:
            self.main -= 1

    def handle_data(self, data):
        inicio = self._pos()
        self._guardar("texto", data, inicio, inicio + len(data))

    def _entidade(self, prefixo, nome):
        inicio = self._pos()
        fim = inicio + len(prefixo) + len(nome)
        if self.fonte.startswith(";", fim):
            fim += 1
        self._guardar("entidade", unescape(self.fonte[inicio:fim]), inicio, fim)

    def handle_entityref(self, name):
        self._entidade("&", name)

    def handle_charref(self, name):
        self._entidade("&#", name)


def _montar(fonte, pedacos, elementos=()):
    texto, inicios, fins = [], [], []

    def por(caracteres, a, b):
        for c in caracteres:
            texto.append(c)
            inicios.append(a)
            fins.append(b)

    quebra = marca = espaco = None  # o que fica pendente até o próximo caractere visível
    for tipo, s, a, b, _ in pedacos:
        if tipo == "bloco":
            quebra, espaco = ("\n\n", a, b), None
            if s:
                marca = (s, a, b)
            continue
        if tipo == "linha":
            quebra, espaco = quebra or ("\n", a, b), None
            continue
        for i, c in enumerate(s):
            ca, cb = (a + i, a + i + 1) if tipo == "texto" else (a, b)
            if c.isspace():
                if texto and quebra is None and espaco is None:
                    espaco = (ca, cb)
                continue
            if quebra and texto:
                por(*quebra)
            if marca:
                por(*marca)
            if espaco:
                por(" ", *espaco)
            quebra = marca = espaco = None
            por(c, ca, cb)
    return Pagina(fonte, "".join(texto), tuple(inicios), tuple(fins), elementos)
