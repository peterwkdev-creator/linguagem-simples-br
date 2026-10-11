"""Detectores dos incisos automáticos do art. 5º.

Cada detector recebe o texto e devolve ocorrências com a posição no texto
original. O limiar de cada um vem de ``limiares.py``, com a fonte; quem usa
pode trocar. O resultado aponta trechos para revisão: não certifica que um
texto cumpre a lei.
"""

import bisect
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from . import limiares
from .pagina import Pagina
from .texto import PARAGRAFO, blocos, palavras


@dataclass(frozen=True)
class Ocorrencia:
    inciso: str
    inicio: int
    fim: int
    trecho: str
    mensagem: str
    medida: int = 0
    no_html: tuple = ()  # (início, fim) no HTML, quando o achado é marcação (XVII)


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


def _ler_lexico(nome):
    """Léxico em ``lexicos/``: uma entrada por linha, "palavra | dado |
    fonte" (o dado é o verbo, a classe...); linha com # é comentário."""
    entradas = {}
    caminho = Path(__file__).parent / "lexicos" / nome
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        palavra, dado, _fonte = (c.strip() for c in linha.split("|", 2))
        entradas[palavra] = dado
    return entradas


# Sigla: duas ou mais maiúsculas (dígito no meio vale), plural em "s"
# minúsculo. Sigla com minúscula no meio ("CNPq", "UnB") fica de fora.
_SIGLA = re.compile(r"(?<!\w)([A-ZÀ-ÖØ-Ý][A-ZÀ-ÖØ-Ý0-9]*[A-ZÀ-ÖØ-Ý][A-ZÀ-ÖØ-Ý0-9]*)(s?)(?!\w)")
_ROMANO = re.compile(r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")
_ANTES_DE_ROMANO = frozenset(
    "inciso incisos capítulo capítulos título títulos anexo anexos seção "
    "seções século séculos parte livro".split()
)
_PALAVRA_SIMPLES = re.compile(r"\w+")
_SEQUENCIA_MAIUSCULA = 3  # palavras em caixa alta seguidas: é texto gritado, não sigla
# Endereço: URL ("https://...%C2%BA") ou e-mail; o domínio se vê pelo ponto.
_SINAL_DE_ENDERECO = re.compile(r"://|@")
# Palavra comum em caixa alta ("SISTEMA SIMEC") se reconhece por aparecer em
# minúscula no mesmo texto. Com quatro letras ou menos, sigla e palavra se
# confundem (MAPA, o ministério, e "mapa"): a regra só vale de cinco em diante.
_MINIMO_PALAVRA_COMUM = 5
# Nome de cor em caixa alta ("VERMELHO - Emergência, LARANJA - Muito Urgente"),
# que a regra acima não pega quando a cor não aparece em minúscula.
_CORES = frozenset(_ler_lexico("cores.txt"))
# Epígrafe de ato normativo, "grafada em caracteres maiúsculos" (LC 95/1998,
# art. 4º): o "DE" e o mês da data ("RDC Nº 513, DE 27 DE MAIO DE 2021")
# não são sigla. O "DE" do ano já sai como texto gritado ("MAIO DE 2021").
_MESES = "JANEIRO FEVEREIRO MARÇO ABRIL MAIO JUNHO JULHO AGOSTO SETEMBRO OUTUBRO NOVEMBRO DEZEMBRO"
_DATA_DE_EPIGRAFE = re.compile(r"\bDE\s+\d{1,2}º?\s+DE\s+(?:%s)\b" % "|".join(_MESES.split()))


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


# Quanto se olha em volta da sigla. Ler a linha ou o texto inteiro a cada
# sigla crescia com o quadrado do tamanho: 2 mil siglas em 104 KB, 21 s.
_JANELA = 300


def _letra(c):
    return c.isalnum() or c == "_"  # o \w das regex


def _em_texto_gritado(texto, inicio, fim):
    """A sigla faz parte de uma sequência de palavras em caixa alta (título
    ou aviso escrito todo em maiúsculas)?"""
    janela = max(0, inicio - _JANELA)
    linha_ini = texto.rfind("\n", janela, inicio) + 1 or janela
    linha_fim = texto.find("\n", fim, fim + _JANELA)
    linha_fim = min(len(texto), fim + _JANELA) if linha_fim == -1 else linha_fim
    # A janela corta palavra no meio: o pedaço fica de fora.
    while linha_ini > 0 and _letra(texto[linha_ini - 1]) and _letra(texto[linha_ini]):
        linha_ini += 1
    while linha_fim < len(texto) and _letra(texto[linha_fim - 1]) and _letra(texto[linha_fim]):
        linha_fim -= 1
    linha = [m for m in _PALAVRA_SIMPLES.finditer(texto, linha_ini, linha_fim)]
    k = next((i for i, m in enumerate(linha) if m.start() == inicio), None)
    if k is None:
        return False
    a = k
    while a > 0 and _caixa_alta(linha[a - 1].group()):
        a -= 1
    b = k
    while b + 1 < len(linha) and _caixa_alta(linha[b + 1].group()):
        b += 1
    return b - a + 1 >= _SEQUENCIA_MAIUSCULA


def _em_endereco(texto, inicio, fim):
    """O trecho faz parte de um endereço: URL, e-mail ou domínio ("GOV.BR")."""
    a = inicio
    while a > 0 and not texto[a - 1].isspace():
        a -= 1
    b = fim
    while b < len(texto) and not texto[b].isspace():
        b += 1
    if _SINAL_DE_ENDERECO.search(texto, a, b):
        return True
    ponto_antes = inicio >= 2 and texto[inicio - 1] == "." and texto[inicio - 2].isalnum()
    ponto_depois = fim + 1 < len(texto) and texto[fim] == "." and texto[fim + 1].isalnum()
    return ponto_antes or ponto_depois


# As letras que o re.I iguala a uma letra ASCII sem ser ela: "İ", "ı", "ſ"
# e o sinal de Kelvin.
_CAIXA_ASCII = str.maketrans({"İ": "I", "ı": "I", "ſ": "S", "K": "K"})


class _Palavras:
    """Onde está cada palavra do texto, lido uma vez só: tal como escrita e
    em caixa alta. Procurar a sigla no texto inteiro a cada sigla nova
    crescia com o quadrado do tamanho."""

    def __init__(self, texto):
        self.exata, self.caixa = {}, {}
        for m in _PALAVRA_SIMPLES.finditer(texto):
            w, onde = m.group(), m.span()
            self.exata.setdefault(w, []).append(onde)
            self.caixa.setdefault(w.translate(_CAIXA_ASCII).upper(), []).append(onde)


def _palavra_comum(texto, sigla, palavras):
    """A "sigla" aparece em minúscula no texto, solta e fora de endereço: é
    palavra comum escrita em caixa alta ("SISTEMA SIMEC" e "o sistema").
    Colada a hífen ou barra é nome de sistema ou caminho
    ("inspecao/e-sisbi"), e não conta."""
    if len(sigla) < _MINIMO_PALAVRA_COMUM:
        return False
    for a, b in palavras.exata.get(sigla.lower(), ()):
        if texto[a - 1:a] in ("/", "-") or texto[b:b + 1] in ("/", "-"):
            continue
        if not _em_endereco(texto, a, b):
            return True
    return False


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
_LIGA_PARENTESE = re.compile(r"\((?:\s*[a-zà-öø-ÿ]+){0,2}\s*$")
_LIGA_TRAVESSAO = re.compile(r"\s[-–—]\s*$")
_CONECTIVOS = frozenset("de da do das dos e em para".split())
# Dentro do nome próprio, também a contração de "em": "Saúde e Segurança no
# Trabalho". No nome ligado, contam como palavra pulada ("Colégio Estadual na
# Rua Nova do Porto - CEP" não serve a CEP).
_LIGAM_NOME = _CONECTIVOS | frozenset("no na nos nas".split())
# Palavra que só tem maiúscula por abrir a frase: "A Guia de Recolhimento".
_ABRE_FRASE = _LIGAM_NOME | frozenset("a o as os ao à pela pelo um uma".split())
# Palavras com maiúscula separadas só por espaço, com um conectivo entre elas;
# o hífen separa palavras ("Procuradoria-Geral", "Coordenação-geral").
_PALAVRA_MAIUSCULA = r"[A-ZÀ-ÖØ-Ý][a-zà-öø-ÿA-ZÀ-ÖØ-Ý]*(?:-[a-zà-öø-ÿA-ZÀ-ÖØ-Ý]+)*"
_NOME_PROPRIO = re.compile(
    r"%s(?:[ \t]+(?:(?:%s)[ \t]+)?%s)*" % (_PALAVRA_MAIUSCULA, "|".join(_LIGAM_NOME), _PALAVRA_MAIUSCULA))
# O fim de um nome maior só serve a sigla de três letras ou mais: com duas, a
# coincidência é comum ("Cadastro de Pessoa Física" e a PF de Polícia Federal,
# "Ambulatório de Pediatria Especializada" e o PE de Pernambuco, nas 90
# páginas das amostras).
_MINIMO_FIM_DO_NOME = 3


_FECHA_PARENTESE = re.compile(r"\s*\)")


def _nome_antes(texto, inicio, fim, sigla, nomes):
    """O nome por extenso vem antes: ligado à sigla (entre parênteses ou com
    travessão) ou, em qualquer ponto antes, como nome próprio cujas
    iniciais são as letras da sigla ("Guia de Recolhimento da União").
    ``nomes`` são os nomes próprios do texto (``_Nomes``)."""
    janela = max(0, inicio - _JANELA)
    m = _LIGA_TRAVESSAO.search(texto, janela, inicio)
    if not m and _FECHA_PARENTESE.match(texto, fim):
        m = _LIGA_PARENTESE.search(texto, janela, inicio)
    if m:
        comeco_frase = max(texto.rfind(".", 0, m.start()), texto.rfind("\n", 0, m.start()))
        if _prefixos_batem(sigla, _PALAVRA_SIMPLES.findall(texto, comeco_frase + 1, m.start())):
            return True
    return nomes.antes(inicio, sigla)


def _letras_da_sigla(sigla):
    return "".join(c for c in _sem_acento(sigla).upper() if c.isalpha())


def _colado(texto, inicio):
    """Onde acaba o texto antes da sigla, sem os espaços que os separam."""
    while inicio > 0 and texto[inicio - 1] in " \t":
        inicio -= 1
    return inicio


def _iniciais_do_nome(nome):
    """As iniciais do nome inteiro (k = 0) e as de cada fim dele que vem
    depois de um conectivo (k > 0), sem os conectivos."""
    nome = re.split(r"[ \t-]+", nome)
    if nome[0].lower() in _ABRE_FRASE:
        nome = nome[1:]
    for k in range(len(nome)):
        if k > 0 and nome[k - 1] not in _LIGAM_NOME:
            continue
        yield k, "".join(_sem_acento(p)[0].upper() for p in nome[k:] if p not in _LIGAM_NOME)


def _nome_proprio_antes(texto, comeco, inicio, sigla):
    """Um nome próprio (palavras com maiúscula ligadas por conectivo, sem
    pontuação nem quebra de linha no meio), entre ``comeco`` e ``inicio``,
    cujas iniciais são as letras da sigla. Vale o nome inteiro ou o fim dele
    depois de um conectivo, se a sigla tem três letras ou mais ("Secretaria
    Especial da Receita Federal do Brasil" serve a RFB), mas não um pedaço
    qualquer: "Informar Mudança de Endereço de Curso" não serve a MEC.
    Colado à sigla, só com espaço entre eles, o nome se lê como o ligado
    ("Divisão de Cooperação e Intercâmbio DICIN")."""
    letras = _letras_da_sigla(sigla)
    colado = _colado(texto, inicio)
    for m in _NOME_PROPRIO.finditer(texto, comeco, inicio):
        if m.end() == colado and _prefixos_batem(sigla, _PALAVRA_SIMPLES.findall(m.group())):
            return True
        for k, iniciais in _iniciais_do_nome(m.group()):
            if iniciais == letras and (k == 0 or len(letras) >= _MINIMO_FIM_DO_NOME):
                return True
    return False


class _Nomes:
    """Os nomes próprios do texto, lidos uma vez só, com as iniciais de cada
    um: procurar de novo antes de cada sigla crescia com o quadrado do
    tamanho do texto. Responde o mesmo que ``_nome_proprio_antes`` desde o
    começo do texto."""

    def __init__(self, texto):
        self.texto = texto
        self.achados = list(_NOME_PROPRIO.finditer(texto))
        self.fins = [m.end() for m in self.achados]
        self.inteiro, self.fim = {}, {}  # iniciais: fim do primeiro nome que as tem
        for m in self.achados:
            for k, iniciais in _iniciais_do_nome(m.group()):
                (self.inteiro if k == 0 else self.fim).setdefault(iniciais, m.end())

    def antes(self, inicio, sigla):
        letras = _letras_da_sigla(sigla)
        if self.inteiro.get(letras, inicio + 1) <= inicio:
            return True
        if len(letras) >= _MINIMO_FIM_DO_NOME and self.fim.get(letras, inicio + 1) <= inicio:
            return True
        i = bisect.bisect_right(self.fins, inicio)  # os nomes antes de i acabam antes da sigla
        if i and self.fins[i - 1] == _colado(self.texto, inicio):
            if _prefixos_batem(sigla, _PALAVRA_SIMPLES.findall(self.achados[i - 1].group())):
                return True
        # o nome que entra na sigla ("Intercâmbio DICIN") se lê só até ela
        if i < len(self.achados) and self.achados[i].start() < inicio:
            return _nome_proprio_antes(self.texto, self.achados[i].start(), inicio, sigla)
        return False


_NOME_DEPOIS = re.compile(r"\s*\(([^()]{3,200})\)")


def _nome_depois(texto, fim, sigla):
    """A sigla vem antes e o nome por extenso depois, entre parênteses?"""
    m = _NOME_DEPOIS.match(texto, fim)
    return bool(m) and _iniciais_batem(sigla, _PALAVRA_SIMPLES.findall(m.group(1)))


def _outra_caixa_antes(texto, inicio, sigla, palavras):
    """A mesma sigla escrita antes em outra caixa: "Secretaria Nacional de
    Trânsito — Senatran" serve ao SENATRAN que vem depois."""
    for a, b in palavras.caixa.get(sigla, ()):
        if b > inicio:
            break
        if re.fullmatch(re.escape(sigla), texto[a:b], re.I):
            yield a, b


def siglas_sem_nome(texto, ignorar=()):
    """Inciso VIII: a primeira vez que a sigla aparece, o nome completo não
    vem antes dela. Aceita o padrão "Nome por Extenso (SIGLA)", em que as
    letras da sigla aparecem, em ordem, nas iniciais do nome."""
    ignorar = {s.upper() for s in ignorar}
    datas = [(d.start(), d.end()) for d in _DATA_DE_EPIGRAFE.finditer(texto)]
    vistas = set()
    achadas = []
    nomes, palavras = _Nomes(texto), _Palavras(texto)
    for m in _SIGLA.finditer(texto):
        sigla = m.group(1)
        if sigla in vistas or sigla in ignorar:
            continue
        if _sem_acento(sigla) != sigla:
            continue  # palavra em caixa alta ("NÃO", "ATENÇÃO"), não sigla
        if _eh_romano(sigla, texto, m.start()) or _em_texto_gritado(texto, m.start(), m.end()):
            continue
        if _em_endereco(texto, m.start(), m.end()) or _palavra_comum(texto, sigla, palavras):
            continue
        if sigla.lower() in _CORES or any(a <= m.start() and m.end() <= b for a, b in datas):
            continue
        vistas.add(sigla)
        if _nome_antes(texto, m.start(), m.end(), sigla, nomes):
            continue
        if any(_nome_antes(texto, a, b, sigla, nomes) for a, b in _outra_caixa_antes(texto, m.start(), sigla, palavras)):
            continue
        if _nome_depois(texto, m.end(), sigla):
            mensagem = f"{sigla}: o nome completo vem depois da sigla; a lei pede antes"
        else:
            mensagem = f"{sigla}: primeira ocorrência sem o nome completo antes"
        achadas.append(Ocorrencia("VIII", m.start(), m.end(), m.group(), mensagem))
    return achadas


# Inciso IX: enumeração dentro do parágrafo. Os guias mandam pôr em tópicos
# a informação que vem dentro de um parágrafo (DICAS p. 2, TJGO p. 7, TRE-AL
# p. 9, Anvisa p. 15; SES-DF p. 6: "Substitua o texto corrido por tópicos").
# O detector vê a forma do par da CAPES p. 7: dois-pontos e itens separados
# por vírgula ou ponto e vírgula na mesma frase. Dois-pontos com menos de 5
# palavras antes é rótulo de campo ("Atenção:", "Endereço:", "Horário:"),
# não frase que anuncia a série: na 11ª amostra (docs/precisao.md), 18
# dos 28 erros e nenhum acerto.
_DOIS_PONTOS = re.compile(r":(?=\s)")
_PALAVRAS_ANTES = 5
_ULTIMO_ITEM = re.compile(r"\s(?:e|ou)\s")
_ABRE_ULTIMO = re.compile(r"(?:e|ou)\s")
_ITEM_NA_LINHA = re.compile(r"[ \t]*\r?\n")


def _itens(serie):
    """Número de itens da série depois dos dois-pontos e onde começa cada
    um. Com ponto e vírgula, só ele separa: a vírgula fica dentro do item.
    Vírgula entre parênteses ou entre algarismos ("R$ 1,50") não separa
    item; na série de vírgulas, o "e" ou o "ou" antes do último item conta
    mais um."""
    separadores, nivel = {",": [], ";": []}, 0
    for i, c in enumerate(serie):
        if c == "(":
            nivel += 1
        elif c == ")":
            nivel = max(nivel - 1, 0)
        elif c in ",;" and nivel == 0 and serie[i + 1:i + 2].isspace():
            separadores[c].append(i + 1)
    comecos = [0] + (separadores[";"] or separadores[","])
    n = len(comecos)
    ultimo = serie[comecos[-1]:].lstrip()
    if not separadores[";"] and not _ABRE_ULTIMO.match(ultimo) and _ULTIMO_ITEM.search(ultimo):
        n += 1
    return n, comecos


def enumeracoes(texto, min_itens=None):
    """Inciso IX: frase de parágrafo com dois-pontos e uma série de itens na
    mesma linha. É um sinal: a lei diz "quando couber", e quem lê decide se
    vira lista ou tabela. Série com um item por linha, item de lista,
    título e rótulo de campo não contam."""
    limite = limiares.valor("IX", min_itens)
    achadas = []
    for bloco in blocos(texto):
        if bloco.tipo != PARAGRAFO:
            continue
        for frase in bloco.frases:
            trecho = frase.em(texto)
            m = next((m for m in _DOIS_PONTOS.finditer(trecho)
                      if len(trecho[:m.start()].split()) >= _PALAVRAS_ANTES), None)
            if not m:
                continue
            serie = trecho[m.end():]
            n, comecos = _itens(serie)
            if n >= limite and not all(_ITEM_NA_LINHA.match(serie, c) for c in comecos):
                achadas.append(Ocorrencia(
                    "IX", frase.inicio, frase.fim, trecho,
                    f"enumeração dentro do parágrafo, {n} itens pela pontuação (limiar: "
                    f"{limite}); o inciso pede lista ou tabela, quando couber", n,
                ))
    return achadas


# Voz passiva analítica: verbo "ser" seguido de particípio. Particípio
# regular (-ado, -ido, -ído) em minúscula, sem acento antes da terminação
# ("válido", "sábado" são adjetivo e substantivo), e os irregulares dos
# exemplos dos guias ("foi entregue", Anvisa p. 14; "é feita", Anvisa p. 13).
_PASSIVA = re.compile(
    r"\b(?i:é|são|foi|foram|era|eram|será|serão|seria|seriam|seja|sejam|"
    r"fosse|fossem|for|forem|ser|sido|sendo)"
    r"\s+(?:\w+mente\s+)?"
    r"(?=[a-zà-öø-ÿ])(\w+(?:ad|id|íd)[oa]s?|entregues?|feit[oa]s?)\b"
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
# Nome de documento logo antes, com "de" sem artigo ("Guia de Recolhimento da
# União", "Documento de identificação"): o substantivo diz que documento é, não
# uma ação. "Pedido de ampliação da indicação" segue apontado (Anvisa, p. 13):
# pedido não é documento.
_DOCUMENTOS = frozenset(_ler_lexico("documentos.txt"))
_DOCUMENTO_ANTES = re.compile(r"(\w+)[ \t]+(?i:de)[ \t]+\Z")
_JANELA_DOCUMENTO = 40


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
    for m in _PALAVRA_SIMPLES.finditer(texto):
        nome = m.group().lower()
        if nome in _NOMINALIZACOES and m.start() not in cobertos and _COMPLEMENTO.match(texto, m.end()):
            antes = _DOCUMENTO_ANTES.search(texto, max(0, m.start() - _JANELA_DOCUMENTO), m.start())
            if antes and antes.group(1).lower() in _DOCUMENTOS:
                continue
            achadas.append(Ocorrencia(
                "XIV", m.start(), m.end(), m.group(),
                f"substantivo no lugar de verbo (verbo: {_NOMINALIZACOES[nome]})",
            ))
    return sorted(achadas, key=lambda o: o.inicio)


# Inciso XV: expressão do léxico (TRE-AL p. 16 e 17, CJF p. 9, CAPES p. 11).
# "*" no fim da palavra vale por qualquer terminação. Entre as palavras,
# espaço ou uma quebra de linha; parágrafo novo, não.
_ESPACO = r"(?:[^\S\n]+|[^\S\n]*\n[^\S\n]*)"


def _padrao_da_expressao(expressao):
    partes = [re.escape(p[:-1]) + r"\w*" if p.endswith("*") else re.escape(p) for p in expressao.split()]
    return re.compile(r"(?<!\w)" + _ESPACO.join(partes) + r"(?!\w)", re.IGNORECASE)


_REDUNDANCIAS = {_padrao_da_expressao(e): forma for e, forma in _ler_lexico("redundancias.txt").items()}


def redundancias(texto):
    """Inciso XV: expressão redundante ou com palavras sobrando, do léxico
    ("Compareça pessoalmente ao local": CAPES p. 11)."""
    achadas = [
        Ocorrencia("XV", m.start(), m.end(), m.group(), f"palavras sobrando: o guia sugere “{forma}”")
        for padrao, forma in _REDUNDANCIAS.items() for m in padrao.finditer(texto)
    ]
    return sorted(achadas, key=lambda o: o.inicio)


# Inciso VI: palavra estrangeira que um guia manda trocar. A barra fica de
# fora como letra ("gov.br/login"): é caminho de endereço, que quem escreve
# o texto não escolhe.
_ESTRANGEIRISMOS = {
    re.compile(r"(?<![\w/])" + _ESPACO.join(map(re.escape, e.split())) + r"(?![\w/])", re.IGNORECASE): forma
    for e, forma in _ler_lexico("estrangeirismos.txt").items()
}


def estrangeirismos(texto):
    """Inciso VI: palavra estrangeira da lista dos guias ("Faça um checklist
    antes de enviar": CAPES p. 9). É sinal: a lei só pede evitar a que não é
    de uso corrente, e quem lê decide."""
    achadas = [
        Ocorrencia("VI", m.start(), m.end(), m.group(), f"palavra estrangeira: o guia sugere “{forma}”")
        for padrao, forma in _ESTRANGEIRISMOS.items() for m in padrao.finditer(texto)
        if not _em_endereco(texto, m.start(), m.end())
    ]
    return sorted(achadas, key=lambda o: o.inicio)


# Inciso IV: palavra pouco comum que um guia manda trocar por outra mais
# conhecida (TJRS p. 31 e 32, CAPES p. 8, Anvisa p. 12, SES-DF p. 9).
_PALAVRAS_COMPLEXAS = {
    _padrao_da_expressao(e): forma for e, forma in _ler_lexico("palavras-complexas.txt").items()
}


def palavras_complexas(texto):
    """Inciso IV: palavra da lista dos guias ("O pedido foi deferido": CAPES
    p. 8). É sinal: o TJRS (p. 31) diz que depende de quem lê, e quem lê
    decide."""
    achadas = [
        Ocorrencia("IV", m.start(), m.end(), m.group(), f"palavra pouco comum: o guia sugere “{forma}”")
        for padrao, forma in _PALAVRAS_COMPLEXAS.items() for m in padrao.finditer(texto)
        if not _em_endereco(texto, m.start(), m.end())
    ]
    return sorted(achadas, key=lambda o: o.inicio)


# Inciso V: termo técnico ou jargão que um guia manda trocar ou explicar
# (TJRS p. 34 e 107, SES-DF p. 10, Anvisa p. 12). Explicado é o que tem a
# explicação logo depois: entre parênteses ("câncer hematológico (no
# sangue)", Anvisa p. 12) ou com "ou seja" e "isto é" até o começo da frase
# seguinte (TJRS p. 34). Explicado na primeira vez, vale para o texto todo
# (TJRS p. 34: "quando colocado pela primeira vez no texto").
_JARGOES = {_padrao_da_expressao(e): forma for e, forma in _ler_lexico("jargoes.txt").items()}
_EXPLICACAO = re.compile(r"[^\S\n]*\(|[^.!?\n]*?(?:[.!?][^\S\n]+)?\b(?:ou seja|isto é|quer dizer)\b", re.IGNORECASE)


def jargoes(texto):
    """Inciso V: termo técnico ou jargão da lista dos guias ("exordial
    acusatória": TJRS p. 107) sem explicação no próprio texto. É sinal: a lei
    aceita o termo explicado, e quem lê decide."""
    achadas = []
    for padrao, forma in _JARGOES.items():
        ocorrencias = list(padrao.finditer(texto))
        if not ocorrencias or _EXPLICACAO.match(texto, ocorrencias[0].end()):
            continue
        achadas += [
            Ocorrencia("V", m.start(), m.end(), m.group(),
                       f"termo técnico ou jargão: o guia sugere “{forma}”, ou explicar no próprio texto")
            for m in ocorrencias if not _EXPLICACAO.match(texto, m.end())
        ]
    return sorted(achadas, key=lambda o: o.inicio)


# Inciso XVII: o que o eMAG 3.1 pede no HTML e se confere sem ver a imagem nem
# seguir o link: texto de link que diz o destino (Recomendação 3.5), texto
# alternativo na imagem (3.6) e célula de cabeçalho na tabela (3.10). O eMAG
# diz que o atributo title não serve de texto do link: não conta.
_LINKS_VAGOS = frozenset(_ler_lexico("links-vagos.txt"))
_PONTAS = re.compile(r"^[\W_]+|[\W_]+$")
_LINK_MARKDOWN = re.compile(r"(?<!!)\[([^\]\n]+)\]\([^)\n]+\)")
_SEM_PAPEL = frozenset({"presentation", "none"})  # role de enfeite ou de leiaute
_LINK_VAGO = "link com texto que não diz o destino (eMAG 3.5)"


def _vago(texto):
    return " ".join(_PONTAS.sub("", texto).split()).casefold() in _LINKS_VAGOS


def acessibilidade(texto):
    """Inciso XVII. Numa ``Pagina``: link de texto vago ("clique aqui",
    eMAG 3.5), imagem sem o atributo alt (3.6) e tabela sem ``th`` (3.10).
    No texto ou Markdown, só o link de texto vago ("[clique aqui](url)")."""
    if not isinstance(texto, Pagina):
        return [
            Ocorrencia("XVII", m.start(), m.end(), m.group(), _LINK_VAGO)
            for m in _LINK_MARKDOWN.finditer(texto) if _vago(m.group(1))
        ]
    achadas = []
    for e in texto.elementos:
        if (e.atributo("role") or "").strip().lower() in _SEM_PAPEL:
            continue
        nomeado = e.atributo("aria-labelledby") is not None
        rotulo = (e.atributo("aria-label") or "").strip()
        if e.tag == "a" and not nomeado and _vago(rotulo or e.texto):
            mensagem = _LINK_VAGO
        elif (e.tag == "img" and e.atributo("alt") is None and not nomeado and not rotulo
              and e.atributo("aria-hidden") != "true"):
            mensagem = "imagem sem texto alternativo, o atributo alt (eMAG 3.6)"
        elif e.tag == "table" and not e.cabecalho:
            mensagem = "tabela sem célula de cabeçalho, o elemento th (eMAG 3.10)"
        else:
            continue
        inicio, fim = texto.no_texto(e.inicio, e.fim)
        trecho = texto.texto[inicio:fim]
        inicio += len(trecho) - len(trecho.lstrip())  # sem a quebra de parágrafo que abre a tabela
        fim -= len(trecho) - len(trecho.rstrip())
        trecho = texto.fonte[e.inicio:e.fim] if e.tag == "img" else texto.texto[inicio:fim]
        achadas.append(Ocorrencia("XVII", inicio, fim, trecho, mensagem, no_html=(e.inicio, e.fim)))
    return achadas
