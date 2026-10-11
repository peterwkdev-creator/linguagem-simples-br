# Segurança

## Como avisar

Falha de segurança não vai em issue pública: use o aviso privado do GitHub,
em [Security → Report a vulnerability](https://github.com/peterwkdev-creator/linguagem-simples-br/security/advisories/new).
Diga a versão, o passo a passo para reproduzir e o efeito.

## O que esperar

- Primeira resposta em até 14 dias.
- A correção sai na última versão publicada; versões antigas não recebem
  correção.
- Crédito no [CHANGELOG.md](CHANGELOG.md) e no aviso, se você quiser.

## O que não é falha de segurança

Resultado diferente do esperado (um valor, uma regra, um caso que falta) é
issue comum, pelo modelo "Resultado diferente do esperado".

A conferência roda sem rede, sem dependências e não grava arquivo. Só a
reescrita (`--reescrever`, `reescrever()`) usa a rede: manda o texto e a
chave a `api.anthropic.com` por HTTPS, sem seguir redirecionamento, e
grava só no `--saida`, sempre arquivo novo. A chave nunca é gravada nem
impressa; se você achar um caminho em que ela aparece ou vai a outro
endereço, isso é falha de segurança.
