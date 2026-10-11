"""Reescrita sugerida por IA, conferida pelo próprio verificador.

A IA (Claude, pela API da Anthropic, com a chave de quem usa) recebe o
texto e os apontamentos do relatório. A reescrita só é aceita se o
verificador medir nela menos apontamentos, nenhum inciso pior, e se todo
número, data, sigla, link e e-mail do original continuar no texto novo,
sem número que o original não tinha. Senão, a IA tenta de novo sabendo o
que falhou; esgotadas as tentativas, a reescrita é recusada e o motivo
vem junto.

O verificador não confere o sentido: quem usa compara o texto novo com o
original antes de usar. Nada aqui é parecer jurídico.

Só a biblioteca padrão: a chamada à API vai pelo ``urllib``.
"""

import json
import os
import re
from dataclasses import dataclass

from .incisos import FONTE_LEI
from .pagina import Pagina
from .relatorio import AVISO, CONFERIDO, conferir, linha_coluna

URL = "https://api.anthropic.com/v1/messages"
VERSAO_DA_API = "2023-06-01"
VARIAVEL_DA_CHAVE = "ANTHROPIC_API_KEY"
MODELO_PADRAO = "claude-sonnet-5-5"
TENTATIVAS = 3  # a primeira e mais duas, sabendo o que falhou
MAX_TOKENS = 16000
TEMPO_LIMITE = 120  # segundos por chamada

AVISO_SENTIDO = (
    "Reescrita sugerida por IA. O verificador confere os apontamentos, os "
    "números, as datas, as siglas e os links, não o sentido: compare com o "
    "original antes de usar."
)

_ENDERECO = re.compile(r"(?:https?://|www\.)[^\s<>\"'()\[\]]+|[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_NUMERO = re.compile(r"\d+(?:[.,/:-]\d+)*")
_SIGLA = re.compile(r"(?<!\w)[A-ZÀ-Ý][A-ZÀ-Ý0-9]*[A-ZÀ-Ý][A-ZÀ-Ý0-9]*(?!\w)")
_TAMANHO_DA_SIGLA = 6  # mais que isso em caixa alta é título ou ênfase, não sigla
_MARCA_DE_ITEM = re.compile(r"^[ \t]*\d{1,3}[.)][ \t]", re.M)  # o "1." da lista numerada
_TEXTO = re.compile(r"<texto>\s*(.*?)\s*</texto>", re.S)


class ErroDeReescrita(Exception):
    """Sem chave, sem rede ou resposta de erro da API."""


@dataclass(frozen=True)
class Reescrita:
    original: str
    texto: str  # o texto novo; vazio quando recusada ou sem nada a reescrever
    aceita: bool
    tentativas: int
    motivo: str  # por que recusou; vazio quando aceita
    antes: tuple  # contagem por inciso conferido: (("II", 3), ...)
    depois: tuple
    modelo: str

    @property
    def total_antes(self):
        return sum(n for _, n in self.antes)

    @property
    def total_depois(self):
        return sum(n for _, n in self.depois)


def reescrever(texto, *, modelo=MODELO_PADRAO, chamar=None, tentativas=TENTATIVAS, **opcoes):
    """Pede à IA uma reescrita de ``texto`` e a confere. ``opcoes`` são as
    de ``conferir`` (``max_palavras``, ``ligar``...), usadas no antes e no
    depois. Com uma ``Pagina``, reescreve só o texto dela. ``chamar``
    substitui a chamada à API: recebe o prompt de sistema e a lista de
    mensagens e devolve a resposta (os testes usam uma IA simulada)."""
    if isinstance(texto, Pagina):
        texto = texto.texto
    chamar = chamar or _chamar_claude(modelo)
    antes = conferir(texto, **opcoes)
    contagem_antes = _contagem(antes)
    if not sum(n for _, n in contagem_antes):
        return Reescrita(texto, "", False, 0, "nenhum apontamento: nada a reescrever",
                         contagem_antes, contagem_antes, modelo)
    mensagens = [{"role": "user", "content": _pedido(texto, antes)}]
    contagem_depois, motivo = contagem_antes, ""
    for tentativa in range(1, tentativas + 1):
        resposta = chamar(_SISTEMA, mensagens)
        novo = _extrair(resposta)
        if novo is None:
            motivo = "a resposta não trouxe o texto entre <texto> e </texto>"
        else:
            depois = conferir(novo, **opcoes)
            contagem_depois = _contagem(depois)
            problemas = _problemas(texto, novo, contagem_antes, contagem_depois)
            if not problemas:
                return Reescrita(texto, novo, True, tentativa, "", contagem_antes, contagem_depois, modelo)
            motivo = "; ".join(problemas)
        mensagens += [
            {"role": "assistant", "content": resposta},
            {"role": "user", "content": _de_novo(motivo, depois if novo is not None else None, novo)},
        ]
    return Reescrita(texto, "", False, tentativas, motivo, contagem_antes, contagem_depois, modelo)


def _contagem(resultados):
    return tuple((r.inciso.numero, len(r.ocorrencias)) for r in resultados if r.estado == CONFERIDO)


def _problemas(original, novo, antes, depois):
    """O que impede aceitar a reescrita; lista vazia quando passa."""
    problemas = []
    total_antes, total_depois = sum(n for _, n in antes), sum(n for _, n in depois)
    if total_depois >= total_antes:
        problemas.append(f"o total de apontamentos não caiu ({total_antes} → {total_depois})")
    depois = dict(depois)
    for inciso, n in antes:
        if depois.get(inciso, 0) > n:
            problemas.append(f"o inciso {inciso} piorou ({n} → {depois[inciso]})")
    sumiram = [t for t in fatos(original) if not _contem(novo, t)]
    if sumiram:
        problemas.append("sumiu do texto: " + ", ".join(sumiram))
    novos = [t for t in _numeros(novo) if t not in _numeros(original)]
    if novos:
        problemas.append("número que o original não tem: " + ", ".join(novos))
    return problemas


def fatos(texto):
    """Links, e-mails, números (com datas e valores) e siglas do texto, na
    ordem em que aparecem e sem repetição: o que a reescrita não pode
    perder."""
    vistos = dict.fromkeys(m.group().rstrip(".,;:!?") for m in _ENDERECO.finditer(texto))
    sem_endereco = _sem_endereco(texto)
    vistos.update(dict.fromkeys(_NUMERO.findall(sem_endereco)))
    vistos.update(dict.fromkeys(s for s in _SIGLA.findall(sem_endereco) if len(s) <= _TAMANHO_DA_SIGLA))
    return list(vistos)


def _numeros(texto):
    return list(dict.fromkeys(_NUMERO.findall(_sem_endereco(texto))))


def _sem_endereco(texto):
    """O texto sem links, e-mails e marcas de lista numerada, onde se
    procuram números e siglas."""
    return _MARCA_DE_ITEM.sub(" ", _ENDERECO.sub(" ", texto))


def _contem(texto, fato):
    # Sem diferença de caixa: "PRAZO" de título que vira "Prazo" não é fato
    # perdido; a sigla que some de todo, sim.
    return re.search(r"(?<![\w.])%s(?!\w)" % re.escape(fato), texto, re.I) is not None


def _extrair(resposta):
    m = _TEXTO.search(resposta)
    return m.group(1) if m else None


_SISTEMA = (
    "Você reescreve textos de órgãos públicos brasileiros em linguagem "
    "simples, conforme o art. 5º da Lei nº 15.263/2025 (Política Nacional "
    "de Linguagem Simples). Regras:\n"
    "- Mantenha todo fato, prazo, valor, data, número, nome, sigla, link e "
    "e-mail do original, escritos do mesmo jeito. Não acrescente informação, "
    "número nem opinião, e não tire direito, dever ou condição.\n"
    "- Na primeira vez que usar uma sigla, escreva o nome completo antes, "
    "com a sigla entre parênteses.\n"
    "- Corrija os trechos apontados pelo verificador sem criar outros "
    "problemas do mesmo tipo.\n"
    "- Mantenha a língua portuguesa e a forma do texto (parágrafos, "
    "listas, títulos). Lista nova vai com hífen, não numerada.\n"
    "Responda só com o texto reescrito, entre <texto> e </texto>, sem "
    "comentário."
)


def _pedido(texto, resultados):
    return (
        "O verificador apontou estes trechos, pelo inciso do art. 5º que "
        "cada um descumpre:\n" + _apontamentos(resultados, texto)
        + "\n\nReescreva o texto abaixo.\n<original>\n" + texto + "\n</original>"
    )


def _de_novo(motivo, resultados, novo):
    pedido = f"A reescrita não foi aceita: {motivo}."
    if resultados is not None and any(r.ocorrencias for r in resultados):
        pedido += "\nNela o verificador ainda aponta:\n" + _apontamentos(resultados, novo)
    return pedido + "\nReescreva de novo a partir do original, entre <texto> e </texto>."


def _apontamentos(resultados, texto):
    linhas = []
    for r in resultados:
        if r.estado != CONFERIDO or not r.ocorrencias:
            continue
        linhas.append(f"Inciso {r.inciso.numero} ({r.inciso.texto}):")
        for o in r.ocorrencias:
            linha, _ = linha_coluna(texto, o.inicio)
            linhas.append(f"- linha {linha}: {o.mensagem}: “{' '.join(o.trecho.split())}”")
    return "\n".join(linhas)


def _chamar_claude(modelo):
    """A chamada à API da Anthropic, pela biblioteca padrão. A chave vem da
    variável de ambiente e só vai no cabeçalho da requisição."""
    def chamar(sistema, mensagens):
        chave = os.environ.get(VARIAVEL_DA_CHAVE, "").strip()
        if not chave:
            raise ErroDeReescrita(f"defina a variável de ambiente {VARIAVEL_DA_CHAVE} com a sua chave da API da Anthropic")
        import urllib.error
        import urllib.request
        corpo = json.dumps({"model": modelo, "max_tokens": MAX_TOKENS, "system": sistema,
                            "messages": mensagens}).encode("utf-8")
        pedido = urllib.request.Request(URL, data=corpo, method="POST", headers={
            "x-api-key": chave, "anthropic-version": VERSAO_DA_API, "content-type": "application/json",
        })
        try:
            with urllib.request.urlopen(pedido, timeout=TEMPO_LIMITE) as resposta:
                dados = json.loads(resposta.read().decode("utf-8"))
        except urllib.error.HTTPError as erro:
            raise ErroDeReescrita(f"a API respondeu {erro.code}: {_mensagem_de_erro(erro)}") from None
        except (urllib.error.URLError, TimeoutError) as erro:
            raise ErroDeReescrita(f"sem resposta da API: {getattr(erro, 'reason', erro)}") from None
        if dados.get("stop_reason") == "max_tokens":
            raise ErroDeReescrita("o texto é longo demais para uma resposta só; divida em partes")
        return "".join(b.get("text", "") for b in dados.get("content", []) if b.get("type") == "text")
    return chamar


def _mensagem_de_erro(erro):
    try:
        return json.loads(erro.read().decode("utf-8"))["error"]["message"]
    except (ValueError, KeyError, TypeError, OSError):
        return erro.reason


def como_dict(r):
    """A reescrita pronta para ``json.dumps``."""
    antes, depois = dict(r.antes), dict(r.depois)
    return {
        "lei": FONTE_LEI, "aviso": AVISO, "aviso_da_reescrita": AVISO_SENTIDO,
        "modelo": r.modelo, "aceita": r.aceita, "tentativas": r.tentativas, "motivo": r.motivo,
        "apontamentos": {"antes": r.total_antes, "depois": r.total_depois if r.aceita else None},
        "por_inciso": [{"inciso": n, "antes": antes[n], "depois": depois[n] if r.aceita else None}
                       for n in antes],
        "texto": r.texto,
    }


def como_texto(r, destino=None):
    """O resumo para a tela; o texto novo vai junto, salvo quando
    ``destino`` diz o arquivo em que foi gravado."""
    linhas = [f"{FONTE_LEI}: reescrita sugerida por IA ({r.modelo})", AVISO, AVISO_SENTIDO, ""]
    if not r.tentativas:
        return "\n".join(linhas + [r.motivo[:1].upper() + r.motivo[1:] + "."])
    if not r.aceita:
        linhas.append(f"Recusada depois de {r.tentativas} tentativas. Na última: {r.motivo}.")
        linhas.append(f"Apontamentos no original: {r.total_antes}. O texto recusado não é mostrado.")
        return "\n".join(linhas)
    linhas.append(f"Aceita na tentativa {r.tentativas}. Apontamentos: {r.total_antes} → {r.total_depois}.")
    depois = dict(r.depois)
    mudou = [(n, a, depois[n]) for n, a in r.antes if a or depois[n]]
    if mudou:
        linhas += ["", "Inciso  antes  depois"] + [f"{n:<7} {a:>5}  {d:>6}" for n, a, d in mudou]
    if destino:
        linhas += ["", f"Texto reescrito gravado em {destino}."]
    else:
        linhas += ["", "Texto reescrito:", "", r.texto]
    return "\n".join(linhas)
