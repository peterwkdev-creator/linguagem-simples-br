"""Relatório dos 18 incisos do art. 5º: o que cada detector achou e o que
não se confere nesta versão, inciso por inciso. Não há nota única: a saída
é sempre por inciso. O relatório aponta trechos para revisão; não é parecer
jurídico e não certifica que um texto cumpre a lei.
"""

from dataclasses import dataclass

from . import limiares
from .detectores import frases_longas, paragrafos_longos, siglas_sem_nome
from .incisos import FONTE_LEI, FORA_DO_ALCANCE, INCISOS, POR_NUMERO, Inciso

AVISO = (
    "O resultado aponta trechos para revisão. Não é parecer jurídico e não "
    "certifica que o texto cumpre a lei."
)

CONFERIDO = "conferido"
SEM_DETECTOR = "sem detector nesta versão"
NAO_CONFERIDO = "não conferido"
DESLIGADO = "desligado"

_TRECHO_MAXIMO = 70  # caracteres do trecho no relatório em texto


@dataclass(frozen=True)
class Resultado:
    inciso: Inciso
    estado: str
    ocorrencias: tuple = ()
    limiar: object = None
    fonte_do_limiar: str = ""


def conferir(texto, max_palavras=None, max_frases=None, ignorar_siglas=(), ligar=(), desligar=()):
    """Um resultado por inciso, na ordem da lei. ``ligar`` e ``desligar``
    recebem números de inciso ("XI"); o XI vem desligado por padrão."""
    ligar, desligar = _numeros(ligar), _numeros(desligar)
    rodar = {
        "II": lambda: frases_longas(texto, max_palavras),
        "III": lambda: paragrafos_longos(texto, max_frases),
        "VIII": lambda: siglas_sem_nome(texto, ignorar_siglas),
    }
    informado = {"II": max_palavras, "III": max_frases}
    resultados = []
    for inciso in INCISOS:
        n = inciso.numero
        if n in desligar or not (inciso.ligado_por_padrao or n in ligar):
            resultados.append(Resultado(inciso, DESLIGADO))
        elif inciso.classe == FORA_DO_ALCANCE:
            resultados.append(Resultado(inciso, NAO_CONFERIDO))
        elif n not in rodar:
            resultados.append(Resultado(inciso, SEM_DETECTOR))
        else:
            limiar, fonte = None, ""
            if n in limiares.LIMIARES:
                limiar = limiares.valor(n, informado[n])
                fonte = limiares.LIMIARES[n].fonte if informado[n] is None else "informado por quem usa"
            resultados.append(Resultado(inciso, CONFERIDO, tuple(rodar[n]()), limiar, fonte))
    return resultados


def _numeros(incisos):
    numeros = {i.strip().upper() for i in incisos}
    desconhecidos = sorted(numeros - POR_NUMERO.keys())
    if desconhecidos:
        raise ValueError(f"inciso desconhecido: {', '.join(desconhecidos)} (use I a XVIII)")
    return numeros


def linha_coluna(texto, posicao):
    """Linha e coluna (a partir de 1) de uma posição do texto."""
    linha = texto.count("\n", 0, posicao) + 1
    coluna = posicao - texto.rfind("\n", 0, posicao)
    return linha, coluna


def como_dict(resultados, texto):
    """Relatório pronto para ``json.dumps``."""
    incisos = []
    for r in resultados:
        item = {
            "inciso": r.inciso.numero,
            "texto_da_lei": r.inciso.texto,
            "classe": r.inciso.classe,
            "estado": r.estado,
        }
        if r.estado == CONFERIDO:
            if r.limiar is not None:
                item["limiar"] = r.limiar
                item["fonte_do_limiar"] = r.fonte_do_limiar
            item["ocorrencias"] = [_ocorrencia(o, texto) for o in r.ocorrencias]
        incisos.append(item)
    return {"lei": FONTE_LEI, "aviso": AVISO, "incisos": incisos}


def _ocorrencia(o, texto):
    linha, coluna = linha_coluna(texto, o.inicio)
    return {
        "inicio": o.inicio, "fim": o.fim, "linha": linha, "coluna": coluna,
        "trecho": o.trecho, "mensagem": o.mensagem, "medida": o.medida,
    }


def como_texto(resultados, texto):
    conferidos = [r for r in resultados if r.estado == CONFERIDO]
    total = sum(len(r.ocorrencias) for r in conferidos)
    linhas = [
        f"{FONTE_LEI}: relatório dos 18 incisos",
        AVISO,
        "",
        f"Conferidos nesta versão: {', '.join(r.inciso.numero for r in conferidos)}. "
        f"Ocorrências: {total}.",
    ]
    for r in resultados:
        linhas += ["", f"{r.inciso.numero}. {r.inciso.texto}", "   " + _situacao(r)]
        for o in r.ocorrencias:
            linha, coluna = linha_coluna(texto, o.inicio)
            linhas.append(f"   - linha {linha}, coluna {coluna}: {o.mensagem}: “{_curto(o.trecho)}”")
    return "\n".join(linhas)


def _situacao(r):
    classe = r.inciso.classe
    if r.estado == DESLIGADO:
        quem = "por padrão" if not r.inciso.ligado_por_padrao else "por quem usa"
        return f"{classe}; desligado {quem}"
    if r.estado == NAO_CONFERIDO:
        return f"{classe}; não conferido: só uma pessoa confere"
    if r.estado == SEM_DETECTOR:
        return f"{classe}; {SEM_DETECTOR}"
    limiar = f"limiar {r.limiar}, fonte: {r.fonte_do_limiar}; " if r.limiar is not None else ""
    n = len(r.ocorrencias)
    achado = "nenhuma ocorrência" if n == 0 else f"{n} ocorrência" + ("s" if n > 1 else "")
    return f"{classe}; {limiar}{achado}"


def _curto(trecho):
    trecho = " ".join(trecho.split())
    if len(trecho) <= _TRECHO_MAXIMO:
        return trecho
    return trecho[:_TRECHO_MAXIMO - 1].rstrip() + "…"
