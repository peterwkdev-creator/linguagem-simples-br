"""Mede a reescrita por IA nos "antes" dos pares dos guias oficiais
(``tests/guias.py``), como em ``docs/precisao.md``.

Uso, da pasta do repositório: ``python docs/medir_reescrita.py medida.jsonl``

A chave vem da variável ``ANTHROPIC_API_KEY`` ou, sem ela, é perguntada no
terminal sem aparecer; não é gravada nem impressa. Cada texto custa uma a
três chamadas à API, cobradas na conta da chave; o total de tokens sai no
fim. O arquivo tem de ser novo e recebe uma linha JSON por texto, na hora
(o que já foi pago não se perde se a medida parar no meio), com o
resultado de ``como_dict``. O sentido de cada reescrita aceita se anota à
parte, à mão.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from linguagem_simples import reescrita  # noqa: E402
from linguagem_simples.__main__ import _perguntar_chave  # noqa: E402
from linguagem_simples.relatorio import conferir  # noqa: E402
from tests import guias  # noqa: E402


def pares():
    for nome, valor in vars(guias).items():
        for i, par in enumerate(valor if isinstance(valor, tuple) else (valor,)):
            if isinstance(par, guias.Par):
                yield (f"{nome}[{i}]" if isinstance(valor, tuple) else nome), par


def main(destino):
    # o arquivo antes da chave: quem digitou a chave não descobre só depois
    # que o nome já existe
    try:
        arquivo = open(destino, "x", encoding="utf-8")
    except FileExistsError:
        return f"medir_reescrita: {destino} já existe; escolha outro nome (a medida nunca grava por cima)"
    try:
        chave = _perguntar_chave()
    except reescrita.ErroDeReescrita as erro:
        arquivo.close()
        Path(destino).unlink()
        return f"medir_reescrita: {erro}"
    textos = aceitas = antes = depois = entrada = saida = 0
    with arquivo:
        for nome, par in pares():
            if not sum(len(r.ocorrencias) for r in conferir(par.antes)):
                continue
            inicio = time.time()
            try:
                r = reescrita.reescrever(par.antes, chave=chave)
            except reescrita.ErroDeReescrita as erro:
                print(f"{nome}: {erro}", file=sys.stderr)
                entrada, saida = entrada + erro.tokens[0], saida + erro.tokens[1]
                if not textos:  # o primeiro já falhou: chave, crédito ou rede
                    arquivo.close()
                    Path(destino).unlink()  # vazio: para rodar de novo com o mesmo nome
                    return 2
                item = {"par": nome, "erro": str(erro), "tokens": {"entrada": erro.tokens[0], "saida": erro.tokens[1]}}
            else:
                item = {"par": nome, "guia": par.fonte.guia, "pagina": par.fonte.pagina, "antes": par.antes,
                        "depois_do_guia": par.depois, **reescrita.como_dict(r),
                        "segundos": round(time.time() - inicio, 1)}
                for repetido in ("lei", "aviso", "aviso_da_reescrita"):
                    del item[repetido]
                entrada, saida = entrada + r.tokens[0], saida + r.tokens[1]
                if r.aceita:
                    aceitas, antes, depois = aceitas + 1, antes + r.total_antes, depois + r.total_depois
                # na recusada, o "depois" é o de uma tentativa que não se entrega
                print(nome, f"aceita, {r.total_antes} → {r.total_depois}" if r.aceita else "recusada",
                      f"({r.tentativas} tentativas)", flush=True)
            textos += 1
            arquivo.write(json.dumps(item, ensure_ascii=False) + "\n")
            arquivo.flush()
    print(f"{textos} textos; {aceitas} aceitas; apontamentos nas aceitas: {antes} → {depois}; "
          f"tokens: {entrada} de entrada e {saida} de saída. Gravado em {destino}.")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
