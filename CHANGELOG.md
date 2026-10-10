# Histórico de versões

A versão segue `linguagem_simples.__version__`; cada uma tem uma tag
`vX.Y.Z` no commit que a publicou. O formato do relatório e as opções da
linha de comando só mudam numa versão 2; detector novo sai numa 1.x.

## 1.2.0 — 10/10/2026

- XVII: o léxico de links vagos passa de 14 para 46 entradas, todas com
  fonte no eMAG 3.1, Recomendação 3.5: formas da mesma regra ("acesse",
  "ver detalhes", "mais informações"), verbo sem o objeto ("Consultar",
  "Solicitar") e o aparelho no lugar do destino ("Android", "iOS").
  "Mais informações" e "Iniciar", sozinhos no link, passam a ser
  apontados.
- Cobertura do XVII medida pela primeira vez: nas 150 páginas, 19% dos
  nomes de link vagos com o léxico da 1.1.0; em 30 páginas novas, 28%
  (12–51) com o léxico novo, que seguiu sem apontar nome que diz o
  destino. Método e números em `docs/precisao.md`.
- Lei reconferida em 10/10/2026 (ficha do Senado): sem alteração.

## 1.1.0 — 10/10/2026

- Detector do inciso XVII (acessibilidade, classe **sinal**), pelo eMAG
  3.1: no HTML, link de texto vago ("clique aqui", "saiba mais"; 3.5),
  imagem sem `alt` (3.6) e tabela sem `th` (3.10); no texto e no Markdown,
  só o link vago. Léxico `lexicos/links-vagos.txt`, 14 entradas com a
  fonte.
- `conferir` aceita a página de `ler_html` no lugar do texto; o achado de
  marcação dá linha e coluna da tag no HTML.
- Precisão do XVII medida nas 150 páginas do gov.br: 98% (90% a 100%).
- README na ordem de quem chega, com selos de testes, versão e licença; o
  histórico da precisão passa a `docs/precisao.md`.
- Texto da lei reconferido em 10/10/2026: sem alteração desde a publicação.

## 1.0.0 — 10/10/2026

- Primeira versão pública: relatório dos 18 incisos do art. 5º da Lei nº
  15.263/2025, em texto ou JSON, de arquivo de texto, Markdown ou HTML.
- Detectores dos incisos II, III, VIII, XII, XIV e XV; o XIII só aponta
  trechos para quem lê decidir; o XI vem desligado por padrão.
- Precisão medida em páginas de serviço do gov.br: XII 100%, XV 98%, II
  95%, XIV 88%, VIII 78%; XIII 31%.
- Opção `--version` (ou `--versao`).
- Texto da lei reconferido em 10/10/2026: sem alteração desde a publicação.
