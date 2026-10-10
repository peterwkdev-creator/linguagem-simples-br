"""Adaptador da vitrine: liga a biblioteca à página (modelo da Coordenação).

Contrato: executar(entradas) recebe {nome do campo: texto} e devolve um dict
com "resumo" (obrigatório; é o que o leitor de tela anuncia), e, se houver,
"aviso", "marcas" (inicio/fim em caracteres do campo_marcado, rotulo,
detalhe) e "tabela" (titulo, colunas, linhas). `vitrine/montar.py` confere o
formato com o exemplo antes de montar.

O que começa por uma tag ("<") se lê como HTML: aí o XVII confere links,
imagens e tabelas, e cada marca cai no HTML colado, que é o que o campo
mostra.
"""
from linguagem_simples.pagina import ler_html
from linguagem_simples.relatorio import CONFERIDO, como_dict, conferir


def executar(entradas):
    texto = entradas["texto"]
    origem = ler_html(texto) if texto.lstrip().startswith("<") else texto
    d = como_dict(conferir(origem), origem)
    marcas, linhas = [], []
    for i in d["incisos"]:
        ocorrencias = i.get("ocorrencias", [])
        for o in ocorrencias:
            marcas.append({"inicio": o["inicio"], "fim": o["fim"],
                           "rotulo": f"Inciso {i['inciso']}", "detalhe": o["mensagem"]})
        linhas.append([i["inciso"], i["texto_da_lei"], i["estado"],
                       len(ocorrencias) if i["estado"] == CONFERIDO else "—"])
    conferidos = sum(1 for i in d["incisos"] if i["estado"] == CONFERIDO)
    n = len(marcas)
    resumo = (f"{n} {'trecho marcado' if n == 1 else 'trechos marcados'}; "
              f"{conferidos} dos {len(d['incisos'])} incisos conferidos nesta versão.")
    return {
        "resumo": resumo,
        "aviso": f"{d['aviso']} Fonte: {d['lei']}.",
        "marcas": marcas,
        "tabela": {"titulo": "Os incisos do art. 5º, um por um",
                   "colunas": ["Inciso", "O que a lei pede", "Situação", "Trechos"],
                   "linhas": linhas},
    }
