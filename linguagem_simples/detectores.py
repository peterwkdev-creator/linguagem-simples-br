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
_SIGLA = re.compile(r"(?<!\w)([A-ZÀ-Ý][A-ZÀ-Ý0-9]*[A-ZÀ-Ý][A-ZÀ-Ý0-9]*)(s?)(?!\w)")
_ROMANO = re.compile(r"M{0,3}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3})")
_ANTES_DE_ROMANO = frozenset(
    "inciso incisos capítulo capítulos título títulos anexo anexos seção "
    "seções século séculos parte livro".split()
)
_PALAVRA_SIMPLES = re.compile(r"\w+")
_SEQUENCIA_MAIUSCULA = 3  # palavras em caixa alta seguidas: é texto gritado, não sigla
# Endereço: URL ("https://...%C2%BA") ou e-mail; o domínio se vê pelo ponto.
_ENDERECO = re.compile(r"://|@")
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


def _em_endereco(texto, inicio, fim):
    """O trecho faz parte de um endereço: URL, e-mail ou domínio ("GOV.BR")."""
    a = inicio
    while a > 0 and not texto[a - 1].isspace():
        a -= 1
    b = fim
    while b < len(texto) and not texto[b].isspace():
        b += 1
    if _ENDERECO.search(texto, a, b):
        return True
    ponto_antes = inicio >= 2 and texto[inicio - 1] == "." and texto[inicio - 2].isalnum()
    ponto_depois = fim + 1 < len(texto) and texto[fim] == "." and texto[fim + 1].isalnum()
    return ponto_antes or ponto_depois


def _palavra_comum(texto, sigla):
    """A "sigla" aparece em minúscula no texto, solta e fora de endereço: é
    palavra comum escrita em caixa alta ("SISTEMA SIMEC" e "o sistema").
    Colada a hífen ou barra é nome de sistema ou caminho
    ("inspecao/e-sisbi"), e não conta."""
    if len(sigla) < _MINIMO_PALAVRA_COMUM:
        return False
    for m in re.finditer(r"(?<![\w/-])%s(?![\w/-])" % re.escape(sigla.lower()), texto):
        if not _em_endereco(texto, m.start(), m.end()):
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
_LIGA_PARENTESE = re.compile(r"\((?:\s*[a-zà-ÿ]+){0,2}\s*$")
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
_PALAVRA_MAIUSCULA = r"[A-ZÀ-Ý][a-zà-ÿA-ZÀ-Ý]*(?:-[a-zà-ÿA-ZÀ-Ý]+)*"
_NOME_PROPRIO = re.compile(
    r"%s(?:[ \t]+(?:(?:%s)[ \t]+)?%s)*" % (_PALAVRA_MAIUSCULA, "|".join(_LIGAM_NOME), _PALAVRA_MAIUSCULA))
# O fim de um nome maior só serve a sigla de três letras ou mais: com duas, a
# coincidência é comum ("Cadastro de Pessoa Física" e a PF de Polícia Federal,
# "Ambulatório de Pediatria Especializada" e o PE de Pernambuco, nas 90
# páginas das amostras).
_MINIMO_FIM_DO_NOME = 3


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
    """Um nome próprio (palavras com maiúscula ligadas por conectivo, sem
    pontuação nem quebra de linha no meio) cujas iniciais são as letras da
    sigla. Vale o nome inteiro ou o fim dele depois de um conectivo, se a
    sigla tem três letras ou mais ("Secretaria Especial da Receita Federal do
    Brasil" serve a RFB), mas não
    um pedaço qualquer: "Informar Mudança de Endereço de Curso" não serve a MEC.
    Colado à sigla, só com espaço entre eles, o nome se lê como o ligado
    ("Divisão de Cooperação e Intercâmbio DICIN")."""
    letras = "".join(c for c in _sem_acento(sigla).upper() if c.isalpha())
    colado = len(antes.rstrip(" \t"))
    for m in _NOME_PROPRIO.finditer(antes):
        if m.end() == colado and _prefixos_batem(sigla, _PALAVRA_SIMPLES.findall(m.group())):
            return True
        nome = re.split(r"[ \t-]+", m.group())
        if nome[0].lower() in _ABRE_FRASE:
            nome = nome[1:]
        for k in range(len(nome) if len(letras) >= _MINIMO_FIM_DO_NOME else 1):
            if k > 0 and nome[k - 1] not in _LIGAM_NOME:
                continue
            if "".join(_sem_acento(p)[0].upper() for p in nome[k:] if p not in _LIGAM_NOME) == letras:
                return True
    return False


def _nome_depois(texto, fim, sigla):
    """A sigla vem antes e o nome por extenso depois, entre parênteses?"""
    m = re.match(r"\s*\(([^()]{3,200})\)", texto[fim:])
    return bool(m) and _iniciais_batem(sigla, _PALAVRA_SIMPLES.findall(m.group(1)))


def _outra_caixa_antes(texto, inicio, sigla):
    """A mesma sigla escrita antes em outra caixa: "Secretaria Nacional de
    Trânsito — Senatran" serve ao SENATRAN que vem depois."""
    return re.compile(r"(?<!\w)%s(?!\w)" % re.escape(sigla), re.I).finditer(texto, 0, inicio)


def siglas_sem_nome(texto, ignorar=()):
    """Inciso VIII: a primeira vez que a sigla aparece, o nome completo não
    vem antes dela. Aceita o padrão "Nome por Extenso (SIGLA)", em que as
    letras da sigla aparecem, em ordem, nas iniciais do nome."""
    ignorar = {s.upper() for s in ignorar}
    datas = [(d.start(), d.end()) for d in _DATA_DE_EPIGRAFE.finditer(texto)]
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
        if _em_endereco(texto, m.start(), m.end()) or _palavra_comum(texto, sigla):
            continue
        if sigla.lower() in _CORES or any(a <= m.start() and m.end() <= b for a, b in datas):
            continue
        vistas.add(sigla)
        if _nome_antes(texto, m.start(), m.end(), sigla):
            continue
        if any(_nome_antes(texto, a.start(), a.end(), sigla) for a in _outra_caixa_antes(texto, m.start(), sigla)):
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
    for m in _PALAVRA_LEXICO.finditer(texto):
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
