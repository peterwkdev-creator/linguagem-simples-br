#!/usr/bin/env bash
# Monta o sdist e o wheel em dist/ e roda o que o pip instala, num venv e
# fora do checkout (de dentro dele, o import pegaria a cópia local). Roda no
# testes.yml a cada push (job "pacote") e no pypi.yml antes de publicar.
# Modelo da Coordenação (modelo/publico/LEIA-ME.md), base no SimplesNacional.
set -euo pipefail
python -m pip install --quiet "build==1.6.1"
python -m build
venv="$RUNNER_TEMP/instalado"
python -m venv "$venv"
"$venv/bin/pip" install --quiet dist/*.whl
cd "$RUNNER_TEMP"
# a versão que o pip instalou é a do __version__ (a CLI responde --version)
v=$("$venv/bin/python" -I -c 'import linguagem_simples as p; print(p.__version__)')
"$venv/bin/python" -I -m linguagem_simples --version | grep -F "$v"
"$venv/bin/linguagem-simples" --version | grep -F "$v"
# com ocorrência o código é 1; o que se confere é o apontamento
printf '<main><p>Para pedir, <a href="/pedir">clique aqui</a>.</p></main>' \
  | "$venv/bin/linguagem-simples" --html - > "$RUNNER_TEMP/saida.txt" || test $? -eq 1
grep -F "clique aqui" "$RUNNER_TEMP/saida.txt"
# Um valor do README, pelo que o pip instalou: o exemplo do HTML pelo
# comando, acima, e pelo import. O XVII lê lexicos/links-vagos.txt, que só
# vai no wheel pelo package-data.
"$venv/bin/python" -I - <<'EOF' | grep -F "XVII clique aqui link com texto que não diz o destino (eMAG 3.5)"
from linguagem_simples.pagina import ler_html
from linguagem_simples.relatorio import conferir

pagina = ler_html('<main><p>Para pedir, <a href="/pedir">clique aqui</a>.</p></main>')
for resultado in conferir(pagina):
    for o in resultado.ocorrencias:
        print(o.inciso, o.trecho, o.mensagem)
EOF
