"""Detectores dos incisos automáticos do art. 5º.

Cada detector recebe o texto e devolve ocorrências com a posição no texto
original. O limiar de cada um vem de ``limiares.py``, com a fonte; quem usa
pode trocar. O resultado aponta trechos para revisão: não certifica que um
texto cumpre a lei.
"""

import re
import unicodedata
from dataclasses import dataclass

from . import limiares
from .texto import PARAGRAFO, blocos, palavras


@dataclass(frozen=True)
class Ocorrencia:
    inciso: str
    inicio: int
    fim: int
    trecho: str
    mensagem: str
    medida: int = 0


def frases_longas(texto, max_palavras=None):
    """Inciso II: frase com mais palavras que o limiar."""
    limite = limiares.valor("II", max_palavras)
    achadas = []
    for bloco in blocos(texto):
        for frase in bloco.frases:
            trecho = frase.em(texto)
            n = len(palavras(trecho))
            if n > limite:
                achadas.append(Ocorrencia(
                    "II", frase.inicio, frase.fim, trecho,
                    f"frase com {n} palavras (limiar: {limite})", n,
                ))
    return achadas


def paragrafos_longos(texto, max_frases=None):
    """Inciso III: parágrafo com mais frases que o limiar. É um sinal de mais
    de uma ideia; item de lista e título não contam como parágrafo."""
    limite = limiares.valor("III", max_frases)
    achadas = []
    for bloco in blocos(texto):
        n = len(bloco.frases)
        if bloco.tipo == PARAGRAFO and n > limite:
            achadas.append(Ocorrencia(
                "III", bloco.inicio, bloco.fim, bloco.em(texto),
                f"parágrafo com {n} frases (limiar: {limite})", n,
            ))
    return achadas


# Sigla: duas ou mais maiúsculas (dígito no meio vale), plural em "s"
# minúsculo. Sigla com minúscula no meio ("CNPq", "UnB") fica de fora.
_SIGLA = re.compile(r"(?<!\w)([A-ZÀ-Ý][A-ZÀ-Ý0-9]*[A-ZÀ-Ý][A-ZÀ-Ý0-9]*)(s?)(?!\w)")
_ROMANO = re.compile(r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")
_ANTES_DE_ROMANO = frozenset(
    "inciso incisos capítulo capítulos título títulos anexo anexos seção "
    "seções século séculos parte livro".split()
)
_PALAVRA_SIMPLES = re.compile(r"\w+")
_SEQUENCIA_MAIUSCULA = 3  # palavras em caixa alta seguidas: é texto gritado, não sigla


def _sem_acento(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def _eh_romano(sigla, texto, inicio):
    if not _ROMANO.fullmatch(sigla):
        return False
    if set(sigla) <= set("IVX"):
        return True
    anterior = re.findall(r"\w+", texto[max(0, inicio - 30):inicio])
    return bool(anterior) and anterior[-1].lower() in _ANTES_DE_ROMANO


def _caixa_alta(palavra):
    letras = [c for c in palavra if c.isalpha()]
    return bool(letras) and all(c.isupper() for c in letras)


def _em_texto_gritado(texto, inicio, fim):
    """A sigla faz parte de uma sequência de palavras em caixa alta (título
    ou aviso escrito todo em maiúsculas)?"""
    linha_ini = texto.rfind("\n", 0, inicio) + 1
    linha_fim = texto.find("\n", fim)
    linha_fim = len(texto) if linha_fim == -1 else linha_fim
    linha = [m for m in _PALAVRA_SIMPLES.finditer(texto, linha_ini, linha_fim)]
    k = next(i for i, m in enumerate(linha) if m.start() == inicio)
    a = k
    while a > 0 and _caixa_alta(linha[a - 1].group()):
        a -= 1
    b = k
    while b + 1 < len(linha) and _caixa_alta(linha[b + 1].group()):
        b += 1
    return b - a + 1 >= _SEQUENCIA_MAIUSCULA


def _iniciais_batem(sigla, palavras_nome):
    """As letras da sigla aparecem, em ordem, nas iniciais das palavras do
    nome? ("Secretaria Especial da Receita Federal do Brasil" serve a RFB.)"""
    letras = [c for c in _sem_acento(sigla).upper() if c.isalpha()]
    i = 0
    for p in palavras_nome:
        if i < len(letras) and _sem_acento(p)[0].upper() == letras[i]:
            i += 1
    return i == len(letras)


def _nome_antes(texto, inicio, fim, sigla):
    """A ocorrência está entre parênteses logo depois do nome por extenso?"""
    antes = texto[:inicio].rstrip()
    depois = texto[fim:].lstrip()
    if not (antes.endswith("(") and depois.startswith(")")):
        return False
    janela = 3 * len(sigla) + 3
    comeco_frase = max(antes.rfind("."), antes.rfind("\n"))
    nome = _PALAVRA_SIMPLES.findall(antes[comeco_frase + 1:-1])[-janela:]
    return _iniciais_batem(sigla, nome)


def _nome_depois(texto, fim, sigla):
    """A sigla vem antes e o nome por extenso depois, entre parênteses?"""
    m = re.match(r"\s*\(([^()]{3,200})\)", texto[fim:])
    return bool(m) and _iniciais_batem(sigla, _PALAVRA_SIMPLES.findall(m.group(1)))


def siglas_sem_nome(texto, ignorar=()):
    """Inciso VIII: a primeira vez que a sigla aparece, o nome completo não
    vem antes dela. Aceita o padrão "Nome por Extenso (SIGLA)", em que as
    letras da sigla aparecem, em ordem, nas iniciais do nome."""
    ignorar = {s.upper() for s in ignorar}
    vistas = set()
    achadas = []
    for m in _SIGLA.finditer(texto):
        sigla = m.group(1)
        if sigla in vistas or sigla in ignorar:
            continue
        if _sem_acento(sigla) != sigla:
            continue  # palavra em caixa alta ("NÃO", "ATENÇÃO"), não sigla
        if _eh_romano(sigla, texto, m.start()) or _em_texto_gritado(texto, m.start(), m.end()):
            continue
        vistas.add(sigla)
        if _nome_antes(texto, m.start(), m.end(), sigla):
            continue
        if _nome_depois(texto, m.end(), sigla):
            mensagem = f"{sigla}: o nome completo vem depois da sigla; a lei pede antes"
        else:
            mensagem = f"{sigla}: primeira ocorrência sem o nome completo antes"
        achadas.append(Ocorrencia("VIII", m.start(), m.end(), m.group(), mensagem))
    return achadas
