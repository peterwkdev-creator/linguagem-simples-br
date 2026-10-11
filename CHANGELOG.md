# Histórico de versões

A versão segue `linguagem_simples.__version__`; cada uma tem uma tag
`vX.Y.Z` no commit que a publicou. O formato do relatório e as opções da
linha de comando só mudam numa versão 2; detector novo sai numa 1.x.

## 1.5.0 — 10/10/2026

- VI: o léxico passa de 24 para 36 entradas com os pares do Guia de
  Linguagem Simples do TJRS (p. 35 e 36): expertise, performance(s), in
  casu, in concreto, in genere, in melius, in natura, ipso facto, ipso
  jure, jus possessionis e jus utendi. Ficam fora da medida de 96%: nas
  520 páginas do gov.br já lidas, aparecem em 2 e acertam nas 2.
- VI: "vide", "status" e "data venia" ficam de fora, como de uso amplo
  (Senado, lista sem itálico; TRF3, "Expressões latinas em textos
  jurídicos"). O README diz por que "upload", "courier", "desktop" e
  outras passam: nenhum guia oficial lido dá a forma a usar no lugar.
- Lei reconferida em 10/10/2026 (ficha do Senado): sem alteração.

## 1.4.0 — 10/10/2026

- Detector do inciso VI (palavras estrangeiras, classe **sinal**): aponta
  a palavra que um guia oficial manda trocar e diz a forma que ele sugere.
  Léxico `lexicos/estrangeirismos.txt`, 24 entradas com a fonte em cada
  linha: CAPES p. 9 (checklist, budget, feedback, deadline, upgrade,
  login, logout), Anvisa p. 12 (experts), TJGO p. 10 (primo ictu oculi) e
  o Manual de Comunicação do Senado (folder, poster, whisky, standard,
  premier, avant-première). Não aponta as que os guias dão como de uso
  corrente, nem a palavra dentro de endereço.
- Precisão do VI: 96% (81–99) em 120 páginas novas do gov.br; cobertura:
  10% (3–30) das palavras estrangeiras para trocar, em 30 delas. Quase
  tudo o que ele aponta é "login". Método e números em
  `docs/precisao.md`.
- Lei reconferida em 10/10/2026 (ficha do Senado): sem alteração.

## 1.3.0 — 10/10/2026

- Detector do inciso IX (texto esquemático, classe **sinal**): frase de
  parágrafo que anuncia uma série depois dos dois-pontos, com 3 itens ou
  mais separados por vírgula ou ponto e vírgula. Fonte: CAPES p. 7 e os
  guias que mandam pôr em tópicos a informação de dentro do parágrafo
  (DICAS, SES-DF, TJGO, TRE-AL, Anvisa). Não conta o dois-pontos de rótulo
  ("Atenção:", menos de 5 palavras antes), a série que já está em linhas
  separadas, nem a de dois itens.
- Precisão do IX: 73% (56–86) em 220 páginas novas do gov.br. A 1ª
  versão, sem a regra do rótulo, tinha dado 43% nas 180 páginas das
  amostras anteriores. Método e números em `docs/precisao.md`.
- README: nos limites, as abas do modelo do gov.br ("O que é?") passam
  sem marca no XVII.
- Lei reconferida em 10/10/2026 (ficha do Senado): sem alteração.

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
