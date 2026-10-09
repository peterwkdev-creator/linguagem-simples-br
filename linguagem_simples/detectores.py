"""Detectores dos incisos automáticos do art. 5º.

Cada detector recebe o texto e devolve ocorrências com a posição no texto
original. O limiar de cada um vem de ``limiares.py``, com a fonte; quem usa
pode trocar. O resultado aponta trechos para revisão: não certifica que um
texto cumpre a lei.
"""

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

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


def _prefixos_batem(sigla, palavras_nome):
    """As letras da sigla saem, em ordem, do começo das palavras do nome,
    uma ou mais de cada ("CEntro de Pesquisa Em Medicina" serve a CEPEM;
    "circuito fechado de TV" serve a CFTV). Depois da primeira letra, o nome
    pula no máximo duas palavras que não sejam conectivo ("Departamento de
    Operações de Comércio Exterior" serve a DECEX; "Coordenação-Geral de
    Autorização para Transferência, Cisão e Retirada", a CGTR)."""
    letras = "".join(c for c in _sem_acento(sigla).upper() if c.isalpha())
    estados = {(0, 0)}  # (letras da sigla já saídas do nome, palavras puladas)
    for palavra in palavras_nome:
        p = _sem_acento(palavra).upper()
        novos = set()
        for i, pulos in estados:
            if i == 0 or palavra in _CONECTIVOS:
                novos.add((i, pulos))
            elif pulos < 2:
                novos.add((i, pulos + 1))
            k = 1
            while k <= len(p) and p[:k] == letras[i:i + k]:
                novos.add((i + k, pulos))
                k += 1
        estados = novos
    return any(i == len(letras) for i, _ in estados)


# Sigla ligada ao nome que vem antes: "Nome (SIGLA)", "Nome (curva SIGLA)"
# ou "Nome - SIGLA" (o hífen de "e-MEC" não liga).
_LIGA_PARENTESE = re.compile(r"\((?:\s*[a-zà-ÿ]+){0,2}\s*$")
_LIGA_TRAVESSAO = re.compile(r"\s[-–—]\s*$")
_CONECTIVOS = frozenset("de da do das dos e em para".split())
# Palavra que só tem maiúscula por abrir a frase: "A Guia de Recolhimento".
_ABRE_FRASE = _CONECTIVOS | frozenset("a o as os na no nas nos ao à pela pelo um uma".split())
# Palavras com maiúscula separadas só por espaço, com um conectivo entre elas.
_NOME_PROPRIO = re.compile(
    r"[A-ZÀ-Ý][a-zà-ÿA-ZÀ-Ý]*(?:[ \t]+(?:(?:%s)[ \t]+)?[A-ZÀ-Ý][a-zà-ÿA-ZÀ-Ý]*)*" % "|".join(_CONECTIVOS))


def _nome_antes(texto, inicio, fim, sigla):
    """O nome por extenso vem antes: ligado à sigla (entre parênteses ou com
    travessão) ou, em qualquer ponto antes, como nome próprio cujas
    iniciais são as letras da sigla ("Guia de Recolhimento da União")."""
    antes = texto[:inicio]
    m = _LIGA_TRAVESSAO.search(antes)
    if not m and texto[fim:].lstrip().startswith(")"):
        m = _LIGA_PARENTESE.search(antes)
    if m:
        cabeca = antes[:m.start()]
        comeco_frase = max(cabeca.rfind("."), cabeca.rfind("\n"))
        if _prefixos_batem(sigla, _PALAVRA_SIMPLES.findall(cabeca[comeco_frase + 1:])):
            return True
    return _nome_proprio_antes(antes, sigla)


def _nome_proprio_antes(antes, sigla):
    """Um nome próprio inteiro (palavras com maiúscula ligadas por conectivo,
    sem pontuação nem quebra de linha no meio) cujas iniciais são as letras da
    sigla: "Informar Mudança de Endereço de Curso" não serve a MEC."""
    letras = "".join(c for c in _sem_acento(sigla).upper() if c.isalpha())
    for m in _NOME_PROPRIO.finditer(antes):
        nome = m.group().split()
        if nome[0].lower() in _ABRE_FRASE:
            nome = nome[1:]
        if "".join(_sem_acento(p)[0] for p in nome if p[0].isupper()) == letras:
            return True
    return False


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


# Voz passiva analítica: verbo "ser" seguido de particípio. Particípio
# regular (-ado, -ido, -ído) em minúscula, sem acento antes da terminação
# ("válido", "sábado" são adjetivo e substantivo), e os irregulares dos
# exemplos dos guias ("foi entregue", Anvisa p. 14; "é feita", Anvisa p. 13).
_PASSIVA = re.compile(
    r"\b(?i:é|são|foi|foram|era|eram|será|serão|seria|seriam|seja|sejam|"
    r"fosse|fossem|for|forem|ser|sido|sendo)"
    r"\s+(?:\w+mente\s+)?"
    r"(?=[a-zà-ÿ])(\w+(?:ad|id|íd)[oa]s?|entregues?|feit[oa]s?)\b"
)
_AGENTE = re.compile(r"\b(?:por|pel[oa]s?)\b(?!\s+meio\b)", re.IGNORECASE)
_FIM_DA_ORACAO = re.compile(r"[,.;:!?]")
_REGULAR = re.compile(r"(\w+?)(?:ad|id|íd)[oa]s?")


def voz_passiva(texto):
    """Inciso XII: verbo "ser" com particípio ("foi entregue pela
    empresa"). A passiva com "-se" ("recomenda-se") fica de fora."""
    achadas = []
    for m in _PASSIVA.finditer(texto):
        regular = _REGULAR.fullmatch(m.group(1))
        if regular and _sem_acento(regular.group(1)) != regular.group(1):
            continue
        resto = texto[m.end():]
        fim = _FIM_DA_ORACAO.search(resto)
        if _AGENTE.search(resto[:fim.start() if fim else len(resto)]):
            mensagem = "voz passiva com agente: na voz ativa, quem faz a ação vira sujeito"
        else:
            mensagem = "voz passiva sem agente: a frase não diz quem faz a ação"
        achadas.append(Ocorrencia("XII", m.start(), m.end(), m.group(), mensagem))
    return achadas


_VIRGULA = re.compile(r",(?=\s)")
_RELATIVO = frozenset({"que", "qual", "quais", "cujo", "cuja", "cujos", "cujas", "onde"})


def frases_intercaladas(texto):
    """Inciso XIII: trecho entre vírgulas, no meio da frase, com pronome
    relativo nas três primeiras palavras ("O documento, que deve ser
    apresentado pelo requerente, é obrigatório": CAPES p. 10)."""
    achadas = []
    for bloco in blocos(texto):
        for frase in bloco.frases:
            virgulas = [v.start() for v in _VIRGULA.finditer(texto, frase.inicio, frase.fim)]
            for a, b in zip(virgulas, virgulas[1:]):
                inicio = [p.lower() for p in palavras(texto[a + 1:b])[:3]]
                if not _RELATIVO.intersection(inicio):
                    continue
                trecho = texto[a + 1:b]
                inicio_do_trecho = a + 1 + len(trecho) - len(trecho.lstrip())
                achadas.append(Ocorrencia(
                    "XIII", inicio_do_trecho, b, texto[inicio_do_trecho:b],
                    "oração intercalada entre vírgulas: a frase fica mais clara em duas ou em ordem direta",
                ))
    return achadas


def _ler_lexico(nome):
    """Léxico em ``lexicos/``: uma entrada por linha, "palavra | verbo |
    fonte"; linha com # é comentário."""
    entradas = {}
    caminho = Path(__file__).parent / "lexicos" / nome
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        palavra, verbo, _fonte = (c.strip() for c in linha.split("|", 2))
        entradas[palavra] = verbo
    return entradas


def _com_plural(nomes):
    formas = {}
    for nome, verbo in nomes.items():
        formas[nome] = verbo
        if nome.endswith("ção"):
            formas[nome[:-3] + "ções"] = verbo
        else:
            formas[nome + "s"] = verbo
    return formas


_NOMINALIZACOES = _com_plural(_ler_lexico("nominalizacoes.txt"))
# Verbo de apoio + substantivo, que o TJGO (p. 12) manda trocar por um verbo
# só: "Faça a identificação" (TJGO p. 12), "Fazer o encaminhamento" (TRE-AL
# p. 15), "promova o recolhimento" e "farão a análise" (Anvisa p. 13).
_APOIO = re.compile(
    r"\b(?i:faz|fazem|fazer|fazemos|fazendo|faça|façam|façamos|fará|farão|"
    r"faria|fariam|fez|fizeram|fizer|fizerem|fizesse|fizessem|feito|feita|"
    r"feitos|feitas|promove|promovem|promover|promovendo|promova|promovam|"
    r"promoverá|promoverão|promoveu|promoveram|promovido|promovida)"
    r"\s+(?i:o|a|os|as|um|uma)\s+(\w+)"
)
_NOMINAL = re.compile(r"\w+(?:ção|ções|mento|mentos)")
_COMPLEMENTO = re.compile(r"\s+(?i:de|do|da|dos|das)\b")
_PALAVRA_LEXICO = re.compile(r"\w+")


def substantivos_no_lugar_de_verbos(texto):
    """Inciso XIV: verbo de apoio com substantivo ("faça a identificação")
    ou substantivo do léxico com complemento ("prevenção da Covid-19"). O
    léxico vem dos guias, com a fonte de cada entrada."""
    achadas = []
    cobertos = set()
    for m in _APOIO.finditer(texto):
        nome = m.group(1).lower()
        if nome in _NOMINALIZACOES or _NOMINAL.fullmatch(nome):
            verbo = _NOMINALIZACOES.get(nome)
            dica = f" (verbo: {verbo})" if verbo else ""
            achadas.append(Ocorrencia(
                "XIV", m.start(), m.end(), m.group(),
                f"verbo de apoio com substantivo: um verbo só diz o mesmo{dica}",
            ))
            cobertos.add(m.start(1))
    for m in _PALAVRA_LEXICO.finditer(texto):
        nome = m.group().lower()
        if nome in _NOMINALIZACOES and m.start() not in cobertos and _COMPLEMENTO.match(texto, m.end()):
            achadas.append(Ocorrencia(
                "XIV", m.start(), m.end(), m.group(),
                f"substantivo no lugar de verbo (verbo: {_NOMINALIZACOES[nome]})",
            ))
    return sorted(achadas, key=lambda o: o.inicio)
