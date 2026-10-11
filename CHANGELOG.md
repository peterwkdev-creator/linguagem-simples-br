# Histórico de versões

A versão segue `linguagem_simples.__version__`; cada uma tem uma tag
`vX.Y.Z` no commit que a publicou. O formato do relatório e as opções da
linha de comando só mudam numa versão 2; detector novo sai numa 1.x.

## 1.9.0 — 11/10/2026

- Comando `linguagem-simples` no PATH depois do `pip install`
  (`linguagem-simples texto.txt`), com as mesmas opções de
  `python -m linguagem_simples`.
- PyPI igual ao GitHub: a página do pacote mostra o GIF e os links do
  README (endereços absolutos); as palavras-chave são os tópicos do
  repositório; a página inicial é a vitrine, com o código, as issues e
  este histórico ao lado; classifiers com as versões do Python (3.11 a
  3.14), a língua e o tema.
- README: selos da versão no PyPI e das versões do Python.
- `SECURITY.md`: como avisar uma falha de segurança sem expô-la (aviso
  privado do GitHub) e o que a biblioteca acessa.
- Actions dos testes e da vitrine fixadas pelo SHA do commit, como as
  da publicação.

## 1.8.0 — 11/10/2026

- A chave da API ficou mais fácil e mais segura: sem a variável
  `ANTHROPIC_API_KEY`, a linha de comando pergunta a chave no terminal,
  sem mostrar o que se cola, e só quando há o que reescrever. Em Python,
  `reescrever(texto, chave=...)`. A chave nunca é gravada nem impressa;
  chave com espaço, quebra de linha ou caractere invisível é recusada sem
  aparecer na mensagem, e a chamada não segue redirecionamento para outro
  endereço.
- Os erros da API dizem o que fazer: chave não aceita, conta sem
  crédito, modelo indisponível, limite de uso, API fora do ar, sem
  internet ou resposta que não é da API (proxy). A mensagem da API vai
  junto.
- A saída mostra os tokens usados, de entrada e de saída, cobrados na
  conta da chave, também quando para num erro depois de uma chamada paga;
  o JSON ganha `tokens` e `do_html`.
- `--saida` recusa arquivo que já existe, `-` e pasta que não existe,
  antes de chamar a IA; se a gravação falhar, o texto aceito vai para a
  tela.
- Num HTML, a saída avisa que só o texto foi reescrito, sem a marcação.
- O pedido à IA marca o texto como dado: ordens dentro dele não devem ser
  obedecidas.
- `docs/medir_reescrita.py` refaz a medida da reescrita, gravando cada
  texto na hora num arquivo novo.
- README: "A chave da API: como funciona", passo a passo.

## 1.7.0 — 11/10/2026

- Reescrita sugerida por IA (`--reescrever`, `reescrita.reescrever`): o
  Claude, com a chave de quem usa (`ANTHROPIC_API_KEY`), reescreve o
  texto a partir dos apontamentos. Só é aceita se o verificador medir
  menos apontamentos, nenhum inciso pior, e se todo número, data, sigla,
  link e e-mail do original continuar, sem número novo; senão, mais duas
  tentativas, e a recusa diz o motivo sem mostrar o texto. `--saida`
  grava o texto aceito, nunca no arquivo lido; `--modelo` troca o modelo
  (padrão `claude-sonnet-5-5`). Só a biblioteca padrão, como antes.
- Medida nos 28 trechos "antes" dos guias oficiais com apontamento: 28
  aceitas, 41 apontamentos → 1; mesmo sentido em 25: 89% (73–96), duas
  passagens às cegas. O verificador não confere o sentido: a saída manda
  comparar com o original.
- Sem mudança no que o verificador aponta.

## 1.6.1 — 11/10/2026

- No PyPI: `pip install linguagem-simples-br`. Publicado pela publicação
  confiável (sem token), a cada Release, depois da aprovação do dono; a
  instalação pela tag continua.
- A cada push, o CI monta o pacote, instala num ambiente limpo e roda um
  exemplo do README que lê um léxico: arquivo de dados fora do pacote
  quebra no push, não na Release.
- Sem mudança no que o verificador aponta.

## 1.6.0 — 11/10/2026

- Detector do inciso IV (palavras comuns, classe **sinal**): aponta a
  palavra pouco comum que um guia oficial manda trocar ("o pedido foi
  deferido", "dez dias ininterruptos") e diz a forma que ele sugere.
  Léxico `lexicos/palavras-complexas.txt`, 86 linhas com a fonte em cada
  uma: TJRS p. 31 e 32 (quadro de palavras complexas), CAPES p. 8 (Dicas
  de substituições), Anvisa p. 12 e SES-DF p. 9. As formas do verbo vêm
  uma a uma onde o radical pegaria outra palavra ("protocolo",
  "requisito", "expediente", "Executivo").
- Precisão do IV: 98% (87–100), 40 de 41, em 490 páginas do gov.br. Em 5
  acertos a forma do guia não cabe ("expedir" no sentido de emitir).
- Detector do inciso V (termos técnicos e jargões, classe **sinal**):
  aponta o termo que um guia manda trocar ou explicar, quando o texto não
  o explica logo depois (entre parênteses, com "ou seja", "isto é" ou
  "quer dizer"); explicado na primeira vez, vale para o texto todo.
  Léxico `lexicos/jargoes.txt`, 32 entradas: TJRS p. 107 e p. 34, SES-DF
  p. 10 e Anvisa p. 12.
- Precisão do V: 8 de 8 (amostra pequena) no gov.br e 1 de 1 em 120
  notícias do CNJ; cobertura 0% (0–5) do jargão do processo nessas
  notícias. Sem marca do V não quer dizer sem jargão.
- Lei reconferida em 11/10/2026 (ficha do Senado): sem alteração.

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
