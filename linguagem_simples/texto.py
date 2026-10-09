"""Divide um texto em blocos (parágrafo, item de lista, título) e frases.

Toda posição é o deslocamento em caracteres no texto original, para o
relatório apontar o trecho exato. Nada aqui é léxico de detector: a lista de
abreviaturas só evita cortar a frase em "art. 5º" ou "Sr. Silva".
"""

import re
from dataclasses import dataclass, field

PARAGRAFO = "parágrafo"
ITEM = "item"
TITULO = "título"

# Ponto depois destas formas não termina a frase (comparação sem caixa).
ABREVIATURAS = frozenset(
    "sr sra srs sras dr dra drs dras prof profa profs av art arts inc "
    "nº n p pp pág págs fl fls ex cf obs aprox tel".split()
)

_SEPARA_BLOCO = re.compile(r"\r?\n[ \t]*(?:\r?\n[ \t]*)+")
_MARCA_ITEM = re.compile(r"[ \t]*(?:[-*•·–]|\d{1,3}[.)]|[a-z][)])[ \t]+")
_MARCA_TITULO = re.compile(r"[ \t]*#{1,6}[ \t]+")
# Fim de frase: pontuação final (com aspas ou parêntese de fecho) seguida de
# espaço e de início de frase, ou do fim do bloco.
_FIM = re.compile(r"[.!?…]+[\"'”’»)\]]*(?=\s+[\"'“‘«(\[]?[A-ZÀ-Ý0-9]|\s*$)")
_PALAVRA = re.compile(r"\w+(?:[-'’.,/:@]\w+)*")
_ANTES_DO_PONTO = re.compile(r"(\w+)\W*$")


@dataclass(frozen=True)
class Trecho:
    inicio: int
    fim: int

    def em(self, texto):
        return texto[self.inicio:self.fim]


@dataclass(frozen=True)
class Bloco(Trecho):
    tipo: str = PARAGRAFO
    frases: tuple = field(default=())


def palavras(texto):
    """Palavras de um trecho. Número com ponto ou vírgula conta como uma."""
    return _PALAVRA.findall(texto)


def _sem_espaco(texto, inicio, fim):
    while inicio < fim and texto[inicio].isspace():
        inicio += 1
    while fim > inicio and texto[fim - 1].isspace():
        fim -= 1
    return inicio, fim


def _eh_abreviatura(texto, inicio, pos_ponto):
    antes = _ANTES_DO_PONTO.search(texto, inicio, pos_ponto)
    if not antes:
        return False
    palavra = antes.group(1)
    # Inicial de nome ("J. Silva") ou abreviatura conhecida.
    return (len(palavra) == 1 and palavra.isupper()) or palavra.lower() in ABREVIATURAS


def frases(texto, inicio, fim):
    """Frases entre ``inicio`` e ``fim`` do texto, sem o espaço das pontas."""
    resultado = []
    comeco = inicio
    for m in _FIM.finditer(texto, inicio, fim):
        if texto[m.start()] == "." and m.end() - m.start() == 1 and _eh_abreviatura(
            texto, comeco, m.start()
        ):
            continue
        a, b = _sem_espaco(texto, comeco, m.end())
        if a < b:
            resultado.append(Trecho(a, b))
        comeco = m.end()
    a, b = _sem_espaco(texto, comeco, fim)
    if a < b and palavras(texto[a:b]):
        resultado.append(Trecho(a, b))
    return tuple(resultado)


def blocos(texto):
    """Blocos do texto: separados por linha em branco; dentro deles, cada
    item de lista e cada título de Markdown é um bloco à parte, e as linhas
    restantes seguidas formam um parágrafo (quebra simples não divide)."""
    resultado = []
    inicio = 0
    limites = [(m.start(), m.end()) for m in _SEPARA_BLOCO.finditer(texto)]
    trechos = []
    for a, b in limites:
        trechos.append((inicio, a))
        inicio = b
    trechos.append((inicio, len(texto)))

    for ini, fim in trechos:
        atual = None  # (tipo, inicio do conteúdo, fim)
        for la, lb in _linhas(texto, ini, fim):
            if not texto[la:lb].strip():
                continue
            item = _MARCA_ITEM.match(texto, la, lb)
            titulo = _MARCA_TITULO.match(texto, la, lb)
            if item or titulo:
                if atual:
                    resultado.append(_fecha(texto, *atual))
                marca = item or titulo
                atual = [ITEM if item else TITULO, marca.end(), lb]
                if titulo:
                    resultado.append(_fecha(texto, *atual))
                    atual = None
            elif atual and atual[0] in (PARAGRAFO, ITEM):
                atual[2] = lb  # continuação da linha anterior
            else:
                atual = [PARAGRAFO, la, lb]
        if atual:
            resultado.append(_fecha(texto, *atual))
    return resultado


def _linhas(texto, inicio, fim):
    """Linhas entre ``inicio`` e ``fim``, sem a quebra (``\\n`` ou ``\\r\\n``)."""
    pos = inicio
    while pos <= fim:
        quebra = texto.find("\n", pos, fim)
        if quebra == -1:
            yield pos, fim
            return
        b = quebra - 1 if quebra > pos and texto[quebra - 1] == "\r" else quebra
        yield pos, b
        pos = quebra + 1


def _fecha(texto, tipo, inicio, fim):
    a, b = _sem_espaco(texto, inicio, fim)
    return Bloco(a, b, tipo=tipo, frases=frases(texto, a, b))
