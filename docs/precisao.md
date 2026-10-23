# Precisão medida

Histórico e método das medições de precisão do
[linguagem-simples-br](../README.md). **Os números atuais estão na tabela
"Precisão medida" do README**; aqui fica cada amostra, na ordem em que
foi medida, com o que mudou entre uma e outra. Por isso a tabela da 1ª
amostra, logo abaixo, tem números que as correções seguintes mudaram.

- [1ª amostra](#1ª-amostra-09102026): o método de todas as medidas.
- [Detectores, amostra por amostra](#detectores-amostra-por-amostra).
- [Reescrita por IA](#reescrita-por-ia): aceite e sentido.

## 1ª amostra (09/10/2026)

Dos trechos que cada detector aponta, quantos uma pessoa, lendo o trecho na
página, confirma. Medido em 09/10/2026, no commit `041d83e`, com os padrões
de fábrica:

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) | Fora da conta: defeito da leitura do HTML |
|---|---|---|---|---|
| II | 95% | 57 / 60 | 86% a 98% | 0 |
| VIII | 77% | 34 / 44 | 63% a 87% | 16 |
| XII | 100% | 59 / 59 | 94% a 100% | 1 |
| XIII | amostra pequena | 1 / 3 | 6% a 79% | 0 |
| XIV | 45% | 23 / 51 | 32% a 59% | 9 |

III não apontou nada nas 30 páginas: sem número.

**Como se mediu.** 30 páginas sorteadas (semente 20261009) entre as 5.735
páginas de serviço do sitemap do gov.br de 08/10/2026. Os 621 apontamentos
viraram 431 sem os repetidos (o modelo do portal se repete em toda página);
de cada inciso, até 60 sorteados. Duas passagens: a segunda às cegas, sem
ver a primeira, com o mesmo critério escrito antes de anotar; 208 dos 243
rótulos iguais (86%), cada divergência resolvida com uma nota. Precisão não
é cobertura: o que o detector deixa passar não entrou nesta conta.

**O que os números dizem:**

- XII acerta a voz passiva; se cada uma deve mudar, a lei deixa a quem
  escreve ("preferencialmente").
- II errava quando a frase apresentava uma lista com marcador "·" no
  mesmo parágrafo: a lista contava como parte da frase. Corrigido: "·"
  marca item de lista.
- VIII: 6 dos 10 erros tinham o nome por extenso antes da sigla, numa
  forma que o detector não reconhecia ("circuito fechado de TV (CFTV)",
  "Coordenação-Geral de Ingresso - CGI"). A correção reconhece 5 deles; o
  sexto pula quatro palavras do nome. Os outros 4 erros são abreviatura de
  mês ("DEZ") e palavra comum em caixa alta, que seguem.
- VIII na amostra nova: dos 10 erros, 6 não são sigla (palavra em caixa
  alta como "SISTEMA" e "SENHA", nome de portal, "BR" de "GOV.BR", pedaço
  de URL) e 4 têm o nome antes numa forma que o detector não liga
  ("Procuradoria-Geral da Fazenda Nacional" antes de "PGFN", "Senatran"
  antes de "SENATRAN", o nome em inglês). O ganho da correção não aparece
  fora da amostra que a motivou: 77% antes, 79% agora, dentro do
  intervalo.
- VIII na 3ª amostra: dos 12 erros, 7 são palavra comum ou rótulo em
  caixa alta que não aparece em minúscula na página ("VERMELHO", "BUSCAR",
  "DEZ", "DE") e 5 têm o nome antes numa forma que o detector não liga
  ("Receita Federal" antes de "RFB", nome colado à sigla sem separador).
  A 2ª correção também não sobe a precisão fora da amostra que a motivou
  (79% antes, 75% agora, dentro do intervalo): o que ela tira está quase
  todo na lista de recomendados, que já ficava fora da conta.
- VIII na 4ª amostra: dos 11 erros, 2 são palavra comum em caixa alta
  ("NORMATIVA", "BUSCAR"). Os outros 9 têm o nome antes. Em 8 deles, as
  letras da sigla não saem das iniciais do nome: sigla em inglês ("Torres
  de Controle de Aeródromo (TWR)") ou que pega sílabas ("CAFIR",
  "JJAER"). No 9º, o nome é o começo de um nome maior ("Domicílio
  Tributário Eletrônico do Simples Nacional e MEI – DTE"). Cada amostra
  nova traz formas novas de escrever o nome antes da sigla: nas quatro
  medidas sem viés, a precisão fica entre 75% e 79% (77%, 79%, 75%, 78%).
- II na amostra nova: os 3 erros são título ou link colado à frase seguinte
  sem ponto; um deles é o título da página somado aos "nomes populares" do
  serviço, que o gov.br põe num `<span>` dentro do título.
- XIV aponta substantivo que nomeia uma coisa, não uma ação. Nome de
  documento com "de" ("Guia de Recolhimento da União") saiu na correção;
  ficam o nome de serviço ("Solicitar Análise de Fotoluminescência") e o
  documento com outra palavra antes do "de" ("Formulário padronizado de
  solicitação", "Requerimento de solicitação de Importação"), o nome de
  sistema ("Solicitação de Divulgação de Informações Aeronáuticas") e a
  solicitação como pedido enviado ("anuência da solicitação"). Na 5ª
  amostra, 3 dos 24 apontamentos foram erro. Use o XIV como lista para
  revisar, não como erro certo.
- Nas páginas do gov.br, a lista "Serviços recomendados para você" está
  dentro do `<main>` e entra no texto lido: dos 60 apontamentos do VIII
  anotados, 16 vinham dela.

## Detectores, amostra por amostra

**Depois da correção (09/10/2026).** Os erros do II e do VIII levaram a
uma correção (abaixo). Nas mesmas 30 páginas e com os mesmos rótulos, a
correção tirou 5 apontamentos do II e 14 do VIII, todos com o nome ou a
lista que o detector antes não via, e não criou nenhum:

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) |
|---|---|---|---|
| II | 100% | 57 / 57 | 94% a 100% |
| VIII | 87% | 34 / 39 | 73% a 94% |

É a mesma amostra que mostrou os erros; por isso estes dois números são
otimistas.

**Amostra nova, sem o viés da correção (09/10/2026, commit `e984809`).**
Outras 30 páginas (semente 2026100902, sem as da primeira), só II e VIII,
mesmo critério e duas passagens (119 dos 120 rótulos iguais). Estes são
os números a usar:

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) | Fora da conta: defeito da leitura do HTML |
|---|---|---|---|---|
| II | 95% | 57 / 60 | 86% a 98% | 0 |
| VIII | 79% | 38 / 48 | 66% a 88% | 12 |

Os 12 de fora estão na lista "Serviços recomendados para você" e no quadro
"Login Integrado" do portal, que a leitura do HTML inclui.

**Terceira amostra, depois da 2ª correção do VIII (09/10/2026).** A 2ª
correção tira do VIII o que não é sigla (endereço, como o "BR" de
"GOV.BR"; palavra que aparece em minúscula no mesmo texto) e liga o nome
com hífen ("Procuradoria-Geral") e a sigla escrita antes em outra caixa
("Senatran" antes de "SENATRAN"). Na 2ª amostra, que a motivou, o VIII foi
a 90% (38 / 42), número otimista. Em outras 30 páginas (semente
2026100903, sem as das duas primeiras), só o VIII, mesmo critério e duas
passagens (49 dos 60 rótulos iguais; as 11 divergências, todas na lista
de recomendados):

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) | Fora da conta: defeito da leitura do HTML |
|---|---|---|---|---|
| VIII | 75% | 36 / 48 | 61% a 85% | 12 |

Medido antes de um ajuste da regra da palavra comum, que tirava uma sigla
verdadeira ("SISBI", por causa do link "inspecao/e-sisbi"); com o ajuste,
o VIII aponta nestas páginas uma sigla a mais.

Depois desta amostra, uma 3ª correção (nome de cor e data da epígrafe de
ato normativo) tira 3 dos 12 erros dela e nenhum acerto: 36 / 45 = 80%
(66% a 89%), número otimista, porque é a amostra que a motivou. Nas
amostras 1 e 2 não muda nada.

Uma 4ª correção liga o nome que vinha antes em três formas que o detector
não via: o fim de um nome maior ("Secretaria Especial da Receita Federal
do Brasil" antes de "RFB"), o nome colado à sigla ("Divisão de Cooperação
e Intercâmbio DICIN") e o nome com "no", "na", "nos" ou "nas" ("Saúde e
Segurança no Trabalho" antes de "SST"). Tira mais 3 erros da 3ª amostra e
nenhum acerto: 36 / 42 = 86% (72% a 93%), também otimista. Nas amostras 1
e 2 não muda nada.

**Quarta amostra, depois da 3ª e da 4ª correções (09/10/2026).** Outras
30 páginas (semente 2026100904, sem as 120 sorteadas antes), só o VIII,
mesmo critério e duas passagens. Desta vez o critério já dizia, antes de
anotar, que item do fim da página é defeito da leitura, e os 60 rótulos
das duas passagens saíram iguais. Este é o número do VIII a usar:

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) | Fora da conta: defeito da leitura do HTML |
|---|---|---|---|---|
| VIII | 78% | 38 / 49 | 64% a 87% | 10 |

Um item ficou fora da conta como dúvida: "ABC", em "Universidade Federal
do ABC". Nestas páginas, as duas correções tiram 7 apontamentos, todos
erros, e nenhum acerto. Mesmo assim, a precisão fica dentro do intervalo
da 3ª amostra, longe dos 86% otimistas.

**Correção do XIV (09/10/2026).** Na 1ª amostra, 16 dos 28 erros do XIV
eram nome de documento: o substantivo vinha depois de "de", sem artigo
("Guia de Recolhimento da União", "Documento de identificação",
"comprovante de pagamento"). A correção deixa de apontar o substantivo
quando a palavra antes do "de" é nome de documento, papel ou informação
(guia, formulário, carteirinha, comprovante, documento, ofício, selo,
cartão, dados; léxico com a acepção do Dicionário Priberam).
"Pedido de ampliação da indicação" (Anvisa) segue apontado. Nas mesmas 30
páginas e com os mesmos rótulos, ela tira 23 apontamentos, 16 deles
anotados, todos erros, e nenhum acerto:

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) |
|---|---|---|---|
| XIV | 66% | 23 / 35 | 49% a 79% |

Número otimista: é a amostra que motivou a correção. Nas 120 páginas das
quatro amostras, ela tira 30 apontamentos, todos nome de documento, e não
cria nenhum.

**Quinta amostra, depois da correção do XIV (09/10/2026, commit
`6c945ed`).** Outras 30 páginas (semente 2026100905, sem as 160 sorteadas
antes), só o XIV, mesmo critério e duas passagens (23 dos 24 rótulos
iguais). Este é o número do XIV a usar:

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) | Fora da conta: defeito da leitura do HTML |
|---|---|---|---|---|
| XIV | 88% | 21 / 24 | 69% a 96% | 0 |

A amostra é pequena: depois da correção, o XIV apontou só 27 vezes nas 30
páginas. Por isso o intervalo é largo. Nestas páginas, a correção tira 5
apontamentos, todos nome de documento, e não cria nenhum.

**XIII nas 150 páginas (09/10/2026, commit `2fbd34e`).** O XIII aponta
pouco: 50 vezes nas 150 páginas das cinco amostras. Os 45 que a 1ª amostra
não tinha anotado foram todos anotados, com o mesmo critério e duas
passagens (41 dos 45 rótulos iguais; 3 ficaram como dúvida):

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) | Fora da conta: defeito da leitura do HTML |
|---|---|---|---|---|
| XIII | 31% | 13 / 42 | 19% a 46% | 0 |

Em 23 dos 29 erros, a oração apontada está no fim da frase. O detector
toma a vírgula seguinte como o fim da intercalação, mas o que vem depois
dela ainda pertence à oração ("Ofício de exigência, que será encaminhado
via SEI, por e-mail, para o interessado"). Use o XIII como lista para
revisar, não como erro certo. Por isso o relatório passou a dar ao XIII a
classe **sinal**.

**XV nas 150 páginas (10/10/2026).** O XV aponta 85 vezes nas 150
páginas; sem os repetidos, 64, dos quais 60 sorteados e anotados com duas
passagens (60 dos 60 rótulos iguais):

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) | Fora da conta: defeito da leitura do HTML |
|---|---|---|---|---|
| XV | 98% | 59 / 60 | 91% a 100% | 0 |

Acerto quer dizer que a forma do guia cabe no lugar sem mudar o sentido.
47 dos 60 são "de acordo com" (47 acertos); os outros 13 são "a fim de",
"com o objetivo de", "com vistas à" e "de conformidade com" (12 acertos).
O erro: "Certificado de conformidade com a norma", em que "conformidade" é
o nome do certificado. Se "de acordo com" é palavra demais, quem diz é o
guia, não esta conta. Os pleonasmos da lista e "compareça pessoalmente"
não apareceram: deles não há número.

**XVII nas 150 páginas (10/10/2026).** O XVII é o primeiro detector que lê
a marcação do HTML: link de texto vago, imagem sem `alt` e tabela sem `th`
(eMAG 3.1, recomendações 3.5, 3.6 e 3.10). Nas 150 páginas das cinco
amostras, sem baixar nada de novo, ele aponta 301 vezes; sem os repetidos,
54, todos anotados com duas passagens (54 dos 54 rótulos iguais):

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) | Fora da conta: defeito da leitura do HTML |
|---|---|---|---|---|
| XVII | 98% | 49 / 50 | 90% a 100% | 4 |

Os 48 links anotados são todos acerto: "Acesse o site" (20), "aqui" (12),
"clique aqui" (6) e outros. O erro é uma tabela de leiaute, com uma célula
vazia, em que o `th` não se aplica; das tabelas, só 2 foram apontadas, e
da imagem nenhuma (as do conteúdo têm `alt`): delas não há número. Os 4 de
fora são o "Saiba mais" do quadro "Login Integrado" do portal, que o modelo
do gov.br põe dentro do `<main>`: é link vago de fato (o `title` não
conta), mas do portal, não do texto do serviço, e soma 163 dos 301
apontamentos. Em várias páginas, o "Acesse o site" é o endereço escrito
que o portal transformou em link com esse texto: continua acerto, porque é
o que o leitor de tela lê.

**Cobertura do XVII nas 150 páginas (10/10/2026).** A precisão diz quanto
do que o XVII aponta é vago; a cobertura diz quanto do que é vago ele
aponta. Nas mesmas 150 páginas, no corpo do serviço, há 1.799 links com
606 nomes distintos. O critério do eMAG 3.5 é o nome lido sozinho, fora da
página, então o mesmo nome tem o mesmo rótulo em toda página: anotaram-se
os 606 (sem sorteio), em duas passagens às cegas, sem saber quais o
detector aponta (599 dos 606 rótulos iguais):

| Inciso | Nomes vagos | Apontados | Cobertura | Intervalo de 95% (Wilson) | Pelos links |
|---|---|---|---|---|---|
| XVII | 43 | 8 | 19% | 10% a 33% | 136 de 805 (17%) |

O léxico é uma lista fechada de 14 expressões ("saiba mais", "clique
aqui", "acesse o site"...): pega as formas mais comuns e não apontou nenhum
nome que diz o destino, mas deixa passar a maior parte dos vagos:

- as quatro abas do modelo do gov.br ("O que é?", "Quem pode utilizar este
  serviço?", "Etapas para a realização deste serviço", "Outras
  Informações"), em todas as páginas, 600 dos 805 links vagos; sem elas
  (conta feita depois de ver o resultado), 8 de 39 nomes (21%) e 136 de
  205 links (66%);
- verbo sem objeto ("Consultar", "Acompanhar", "Preencher", "Emitir");
- plataforma no lugar do destino ("Android", "Apple", "iOS");
- só o tipo do destino ("formulário", "guia", "orientações");
- o apontar fora da forma exata ("Clique aqui para saber mais.", "Acesse
  o sistema").

Ou seja: quando o XVII aponta, quase sempre acerta; quando não aponta, o
link ainda pode ser vago.

**Léxico maior do XVII, em 30 páginas novas (1.2.0, 10/10/2026).** Dos
vagos que passaram, saíram 32 entradas novas, todas pela regra do eMAG
3.5: formas da mesma regra ("acesse", "ver detalhes", "mais
informações"), verbo sem o objeto ("Consultar", "Solicitar") e o aparelho
no lugar do destino ("Android", "iOS"). Nas 150 páginas de onde saíram, o
número é otimista: 23 de 43 nomes vagos (53%), e os 23 apontados são
vagos. Para o número sem esse viés, 30 páginas novas foram sorteadas
antes de baixar (5.535 páginas de serviço que nenhuma amostra tinha
usado). Os 194 nomes de link delas foram anotados do mesmo jeito (192 dos
194 rótulos iguais):

| Léxico | Nomes apontados | Vagos entre eles | Nomes vagos | Cobertura | Intervalo de 95% (Wilson) | Pelos links |
|---|---|---|---|---|---|---|
| 1.1.0 (14 entradas) | 3 | 3 | 18 | 17% | 6% a 39% | 27 de 166 |
| 1.2.0 (46 entradas) | 5 | 5 | 18 | 28% | 12% a 51% | 29 de 166 |

O léxico novo seguiu sem apontar nome que diz o destino (5 de 5; amostra
pequena para dar precisão). O ganho é pequeno: a lista fechada cresce
devagar contra a variedade dos nomes. Passaram "Acesse o serviço",
"Acesso ao Sistema", "Protocolar", "Requerimento" e as quatro abas do
modelo do gov.br (120 dos 166 links vagos; sem elas, depois de ver o
resultado, 5 de 14 nomes, 36%).

**IX, em duas rodadas (1.3.0, 10/10/2026).** O IX aponta a frase de
parágrafo que anuncia uma série depois dos dois-pontos, com 3 itens ou
mais na mesma linha. O detector foi escrito só com os pares dos guias
(CAPES p. 7, DICAS p. 2, SES-DF p. 6), antes de rodar em qualquer página.
Nas 180 páginas das amostras anteriores (sem baixar nada), ele apontou 61
frases distintas; 60 sorteadas foram anotadas com duas passagens (60 dos
60 rótulos iguais). Acerto quer dizer que os itens são paralelos e, um
por linha, formariam lista ou tabela.

| Versão | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) | Fora da conta: defeito da leitura do HTML | Amostra |
|---|---|---|---|---|---|
| 1ª (não publicada) | 43% | 21 / 49 | 30% a 57% | 11 | 180 páginas já usadas |
| 1.3.0 | 73% | 22 / 30 | 56% a 86% | 4 | 220 páginas novas |

Na 1ª, 18 dos 28 erros eram dois-pontos de rótulo de campo ("Atenção:",
"Obs.:", "Endereço:", "Horário:"), com até 4 palavras antes, e nenhum
acerto tinha menos de 5. A 1.3.0 só conta o dois-pontos com 5 palavras ou
mais antes. Naquelas 180 páginas a regra daria 68%, número otimista,
porque foram elas que a sugeriram. Por isso a 1.3.0 foi medida em 220
páginas que nenhuma amostra tinha usado, sorteadas antes de baixar (120,
ampliadas para 220 só pela contagem de apontamentos, antes de anotar).
Os 34 apontamentos distintos foram todos anotados (33 dos 34 rótulos
iguais). Os 8 erros: exemplo entre parênteses, dois itens com "dentre
outras", citações legais, aposto. Os 4 de fora são contato, endereço e
listas que a página já põe em linhas separadas, que a leitura do HTML
juntou. A série de dois itens ("RG e CPF") não é apontada: os pares da
DICAS e da SES-DF passam sem marca.

**Cobertura do IX (1.3.0, 10/10/2026).** A precisão diz quanto do que o
IX aponta é enumeração; a cobertura diz quanto das enumerações ele
aponta. Nas mesmas 220 páginas, um filtro que não usa o detector separou
as frases de parágrafo do corpo do serviço com forma de série: ponto e
vírgula, ou vírgula seguida, em até 8 palavras, de "e" ou "ou" (889
frases distintas). Foram sorteadas 150 (semente 2026101016), e duas
passagens às cegas, sem saber o que o detector aponta, disseram se cada
uma traz 3 itens paralelos ou mais que, um por linha, formariam lista ou
tabela (149 dos 150 rótulos iguais).

| Enumerações | Apontadas | Cobertura | Intervalo de 95% (Wilson) | Fora da conta: a página já põe em lista |
|---|---|---|---|---|
| 59 | 4 | 7% | 3% a 16% | 2 |

52 das 59 não têm dois-pontos ("O pagamento poderá ser realizado via Pix,
cartão de crédito ou boleto bancário"; "Informe seu CPF, o número de
registro da CNH e o código de segurança"), e o detector só lê a série
depois deles. Nas 7 com dois-pontos, aponta 4; escapam um rótulo de 4
palavras ("Selecionar a modalidade pretendida:"), um "Obs.:" e um
dois-pontos colado ao item seguinte por defeito da página. Nenhuma das 89
frases sem enumeração foi apontada. Uma frase de modelo do portal ("Em
caso de dúvidas, reclamações ou sugestões…") aparece em 8 páginas e conta
8 vezes; sem as repetições, são 52 enumerações e as mesmas 4 apontadas.
O filtro não vê a série só com vírgulas, sem "e" nem "ou" no fim, e 11
apontamentos do IX nessas páginas são dessa forma: a medida vale para a
série com "e", "ou" ou ponto e vírgula.

**VI, precisão e cobertura (1.4.0, 10/10/2026).** O VI aponta a palavra
estrangeira que um guia oficial manda trocar: 24 entradas, da CAPES
(p. 9), da Anvisa (p. 12), do TJGO (p. 10) e do verbete "Estrangeirismo"
do Manual de Comunicação do Senado. As 410 páginas das amostras
anteriores serviram para escolher o léxico ("menu" ficou de fora: ali é
sempre o menu da tela) e por isso não medem. A medida foi em 120 páginas
novas, sorteadas antes de baixar (semente 2026101018). O VI apontou 103
vezes, em 63 páginas (login 96, checklist 7); 60 sorteadas. 34 delas são
o título "Login Integrado" do rodapé do portal, fora da conta como defeito
da leitura do HTML; as 26 do corpo do serviço foram anotadas com duas
passagens (26 dos 26 rótulos iguais).

| Medida | Resultado | Intervalo de 95% (Wilson) | Amostra |
|---|---|---|---|
| Precisão | 96% (25 / 26) | 81% a 99% | 120 páginas novas |
| Cobertura | 10% (2 / 20) | 3% a 30% | 30 dessas páginas, lidas inteiras |

O erro é "login único", nome do serviço de entrada do gov.br. Em 11 dos
25 acertos, a sugestão da CAPES não cabe: "login e senha" pede "usuário",
não "acesso". Na cobertura, duas passagens às cegas leram o corpo do
serviço de 30 páginas e listaram cada palavra estrangeira (174 itens, 168
iguais; 6 divergências resolvidas com nota), dizendo se é de uso corrente
ou se há palavra portuguesa tão usada. Das 20 para trocar, o VI aponta os
2 "checklist"; passam courier, upload, vide, in loco, status, campi,
desktop, mobile, packing-list, timecode e termos técnicos em inglês de
uma página da Anac. Das 154 de uso corrente (web, e-mail, site, drone,
link…), o VI aponta 7, todas "login": a CAPES manda trocá-la, mas quem lê
a achou corrente. A lei só pede evitar a palavra que não é de uso
corrente; por isso o VI é sinal.

**V, precisão e cobertura (1.6.0, 11/10/2026).** O V aponta o termo
técnico ou o jargão que um guia manda trocar ou explicar, quando o texto
não o explica logo depois: 32 entradas, 24 do quadro "Expressões que
devem ser evitadas" do TJRS (p. 107), 6 dos exemplos de "Jargões e termos
técnicos" do TJRS (p. 34), "peticionar" (SES-DF p. 10) e "câncer
hematológico" (Anvisa p. 12). Nas 490 páginas do gov.br já lidas, que não
serviram para montar o léxico, apontou 9 vezes, todas "peticionar"; uma
estava na lista "Serviços recomendados para você", fora da conta como
defeito da leitura do HTML. As 8 do corpo do serviço são acerto nas duas
passagens. Para achar o jargão jurídico, a medida seguinte foi em 120
notícias do CNJ, sorteadas antes de baixar (semente 2026101101, entre
44.930): o V apontou 1 vez ("Carta Magna", acerto). Na cobertura, duas
passagens às cegas leram 30 dessas notícias e listaram cada termo técnico
ou jargão sem explicação.

| Medida | Resultado | Intervalo de 95% (Wilson) | Amostra |
|---|---|---|---|
| Precisão | amostra pequena (8 / 8) | 68% a 100% | 490 páginas do gov.br |
| Cobertura | 0% (0 / 77) | 0% a 5% | 30 notícias do CNJ, lidas inteiras |

Os 77 são os termos que as duas passagens listaram sem dúvida; com os
duvidosos, 0 de 126 (0% a 3%). O jargão real é o do processo ("autos",
"liminar", "mérito", "precatórios", "embargos de declaração",
"homologação", "diligências"), e não o do quadro do TJRS, feito de
fórmulas de petição ("exordial acusatória", "consoante o disposto").
Quando o V aponta, acerta; quando não aponta, não quer dizer que não há
jargão.

**IV, precisão (1.6.0, 11/10/2026).** O IV aponta a palavra pouco comum
que um guia manda trocar por outra mais conhecida: 86 linhas, do quadro
de palavras complexas do TJRS (p. 31 e 32), das "Dicas de substituições"
da CAPES (p. 8), da Anvisa (p. 12) e da SES-DF (p. 9), com as formas do
verbo uma a uma onde o radical pegaria outra palavra ("protocolo",
"requisito", "expediente"). O léxico saiu só dos guias, e por isso as
490 páginas do gov.br já lidas servem de amostra: 475 apontamentos, 460
sem os repetidos, em 205 páginas; 60 sorteados (semente 2026101106). 19
estavam no cabeçalho ou no fim da página, fora da conta como defeito da
leitura do HTML; os 41 do corpo do serviço foram anotados com duas
passagens às cegas (41 dos 41 rótulos iguais).

| Medida | Resultado | Intervalo de 95% (Wilson) | Amostra |
|---|---|---|---|
| Precisão | 98% (40 / 41) | 87% a 100% | 490 páginas do gov.br |

O erro é "Protocolar por código de requerimento", nome de uma opção da
tela, entre aspas. Em 5 dos 40 acertos, a palavra é difícil mas a forma
do guia não cabe: 4 de "expedir" no sentido de emitir um documento ("a
licença será expedida"), em que a CAPES dá "mandar, enviar", e 1 de
"decisão proferida". Os mais apontados: "protocolar" (14 dos 60),
"requerer" (6), "deferimento" (4). A cobertura do IV não foi medida: o
que é palavra difícil depende de quem lê (TJRS, p. 31), e a lista do que
falta pede critério próprio.

## Reescrita por IA

**Reescrita por IA, aceite e sentido (1.7.0, 11/10/2026).** A reescrita
(`--reescrever`) rodou nos 28 trechos "antes" dos pares dos guias
(`tests/guias.py`) que têm ao menos um apontamento, de 32 pares; 4 a 68
palavras cada. Modelo `claude-sonnet-5-5`, padrões de fábrica, 73
segundos ao todo.

| Medida | Resultado | Intervalo de 95% (Wilson) |
|---|---|---|
| Aceitas pelo verificador | 28 / 28 (25 na 1ª tentativa, 3 na 2ª) | — |
| Apontamentos | 41 → 1 | — |
| Mesmo sentido | 89% (25 / 28) | 73% a 96% |

Por inciso, antes → depois: XII 9 → 0, XIV 9 → 0, IV 6 → 0, II 5 → 0,
VI 3 → 0, VIII 3 → 1, XIII 3 → 0, V 2 → 0, IX 1 → 0, XV 1 → 0. O que
sobrou é "A DTI vai atender.": o trecho não dá o nome da sigla, e a
reescrita não o inventou. Nenhuma foi recusada nesta medida; a recusa só
está provada nos testes, com IA simulada.

**Como se mediu o sentido.** Critério escrito antes de ver as
reescritas: o sentido é o mesmo quando nenhum fato, prazo, valor,
condição, sujeito, obrigação ou direito mudou ou sumiu, nada foi
acrescentado (salvo o nome por extenso certo da sigla) e ordem continua
ordem. Duas passagens, a segunda às cegas, em outra ordem e sem o nome
dos pares; 25 dos 28 rótulos iguais. As 3 divergências, resolvidas pelo
critério: "Compareça pessoalmente" → "Compareça" fica como mesmo (a
CAPES, p. 11, dá "pessoalmente" como redundante); "dando cumprimento ao
mandado" → "cumpri o mandado" mudou (a certidão passa a afirmar o
cumprimento); "peticionar" → "entrar com uma ação judicial" mudou (a
petição pode não ser ação), embora seja a troca que o guia da SES-DF
(p. 10) faz. A 4ª mudança, nas duas passagens: "O pedido foi deferido"
→ "Aceitamos o pedido" põe quem decidiu, que o original não diz (a
CAPES, p. 8, escreve "O pedido foi aceito").

Limites: trechos curtos, de guias públicos que o modelo pode ter lido.

Para refazer, com a sua chave: `python docs/medir_reescrita.py
medida.jsonl`, da pasta do repositório. O script grava o resultado de
cada trecho numa linha, na hora, num arquivo novo; o sentido se anota à parte, com o critério acima. Desde a
1.8.0, o arquivo traz também os tokens de cada reescrita (esta medida, da
1.7.0, não os registrou).

**Os mesmos 28 sem o pensamento do modelo (1.10.1, 11/10/2026).** A
1.10.1 desliga o pensamento do `claude-sonnet-5-5` (na 1.10.0 ele gastava
o limite de saída numa página longa). Mesmos trechos e critério: 28 / 28
aceitas (2 na 2ª tentativa), 42 → 0 apontamentos (os detectores mudaram
desde a 1.7.0), mesmo sentido em 24 / 28 = **86% (69% a 94%)**, dentro da
margem da 1.7.0. Mudaram: "DTI" ganhou um nome por extenso que o trecho
não dá; "a CAPES organiza" e "Aplique a pomada" põem quem faz, que o
original não diz; "peticionar" virou "entrar com uma ação judicial", como
antes. 19.275 tokens de entrada e 2.007 de saída, 64 segundos ao todo.

**Reescrita de página longa (1.10.1, 11/10/2026).** 10 páginas sorteadas
(semente 20261011) entre as 133 páginas de serviço do gov.br com mil
palavras ou mais, de 490 já baixadas para a precisão; de 1.024 a 1.584
palavras cada, com a moldura do portal (avaliação, ouvidoria), como para
quem usa. Mesmo critério, com uma regra a mais escrita antes: um só fato
mudado faz a página inteira contar como "mudou".

| Medida | Resultado | Intervalo de 95% (Wilson) |
|---|---|---|
| Aceitas pelo verificador | 10 / 10 (7 na 1ª tentativa) | — |
| Apontamentos | 378 → 92 | — |
| Mesmo sentido | 0% (0 / 10) | 0% a 28% |

As duas passagens (a 2ª às cegas, em outra ordem) deram "mudou" nas 10.
Em todas, a reescrita põe quem faz a ação onde a passiva não diz: "Os
números são atualizados diariamente", da moldura, virou "O sistema
atualiza" em 9 e "O IFSP atualiza" em 1 (errado: a avaliação é do
gov.br); numa página de vacinação, "os dados já foram enviados" virou "O
profissional já enviou", e a mesma página diz que quem envia é a gestão
estadual ou municipal. Em 5, as duas passagens acham outra mudança: "campos
em branco ou informação falsa [...] pode configurar crime" virou "A
informação falsa também pode configurar crime" (a omissão sai do crime);
siglas (PSOA, SINTAC, SACI, CHT) ganharam nomes por extenso que a página
não dá, um deles errado; "sujeita à perda do direito" virou "perde o
direito"; o rótulo do ícone "PDF" ganhou o nome por extenso, que não está
na tela. Nenhuma perdeu link, e-mail, telefone, prazo ou valor. 116.264
tokens de entrada e 50.862 de saída; mediana de 19 segundos por página.

**O pedido novo (1.11.0, 11/10/2026).** O pedido à IA ganhou quatro
regras, escritas sem os exemplos da amostra: não dizer quem faz a ação
quando o original não diz; não trocar possibilidade por certeza; pôr o
nome por extenso da sigla só se está no texto ou é certo; não mudar o
nome de link, botão, menu ou campo, nem o título de lei ou artigo. A
regra de decisão foi escrita antes de rodar: o pedido fica se, nas
longas, as páginas com agente acrescentado caírem e as com outra mudança
não subirem, e se nos 28 curtos o sentido não cair abaixo de 69%. Mesmas
amostras, modelo e critério; 2 passagens, a 2ª às cegas (sementes
20261013 e 20261014).

| Medida | 1.10.1 | 1.11.0 |
|---|---|---|
| Curtos: aceitas | 28 / 28 | 28 / 28 |
| Curtos: apontamentos | 42 → 0 | 42 → 4 |
| Curtos: mesmo sentido | 86% (69% a 94%) | **93% (77% a 98%)** |
| Longas: aceitas | 10 / 10 | 10 / 10 |
| Longas: apontamentos | 378 → 92 | 378 → 163 |
| Longas: mesmo sentido | 0% (0% a 28%) | **40% (17% a 69%)** |
| Longas com quem faz a ação acrescentado | 10 / 10 | 4 / 10 |
| Longas com outra mudança | 5 / 10 | 2 / 10 |
| Longas com nome de link trocado | 5 / 10 (contados só "Login Integrado" e o ícone "PDF") | 2 / 10 |

O pedido ficou. Nos curtos, mudaram "peticionar" (de novo "entrar com
uma ação judicial") e "Aplique a pomada", que põe o leitor como quem
aplica; a DTI ficou sigla. Nas longas, quem faz a ação ainda aparece em 4
("Você fará as correções", "A unidade entrega o passaporte"); "são
atualizados diariamente" virou "mudam todos os dias"; a omissão saiu do
crime de novo, e uma condição ("desde que atenda aos requisitos legais")
sumiu; "Login Integrado" e o link "Requerer alteração..." mudaram de
nome. Todas as siglas que ganharam nome por extenso estão certas. A
concordância entre as passagens foi de 25 / 28 e 8 / 10; cada divergência
se resolveu relendo o par (o rótulo, no HTML da página). O custo é mais
apontamento sobrando: a voz passiva (inciso XII) fica em 77 de 121 (18
na 1.10.1) e a sigla (VIII) em 37 de 55 (18). 109.010 tokens de entrada
e 47.780 de saída nas longas; mediana de 16 segundos por página.

**Duas conferências novas (1.12.0, 11/10/2026).** Dois dos erros da
1.11.0 dá para pegar sem ler o sentido: o texto de link mudado e a
alternativa que sai da frase de crime ("campos em branco ou informação
falsa … pode configurar crime" virou "Informação falsa também pode
configurar crime"). A reescrita agora volta à IA nos dois casos. Provas
antes de medir, sem chave: as duas pegam a página 08 e a 05 das medidas
anteriores; o original contra ele mesmo dá zero acusação em 55 textos;
nos 56 curtos, nada. Regra escrita antes: as conferências ficam se toda
recusa, relida, for perda real e as aceitas nas longas não caírem abaixo
de 8 / 10. Mesmas 10 páginas, mesmo pedido e mesmo critério de sentido,
com 2 passagens, a 2ª às cegas (semente 20261015).

| Medida | 1.11.0 | 1.12.0 |
|---|---|---|
| Longas: aceitas | 10 / 10 | 10 / 10 (4 na 2ª tentativa) |
| Longas: apontamentos | 378 → 163 | 378 → 176 |
| Longas: mesmo sentido | 40% (17% a 69%) | **40% (17% a 69%)** |
| Longas com quem faz a ação acrescentado | 4 / 10 | 4 / 10 |
| Longas com outra mudança | 2 / 10 | 4 / 10 |
| Longas com nome de link trocado | 2 / 10 | 1 / 10 (um título, não um link) |

As conferências ficaram. Das três tentativas recusadas por elas, duas
eram link mudado de fato ("Requerer…" virou "Pedir…"). A terceira
dividia a frase do crime e deixava o sujeito na frase anterior. Era
recusa falsa, e por isso a frase de punição que não traz nenhuma
alternativa passou a valer junto com a anterior (provado de novo antes
de publicar). Na medida, a frase do crime e os links ficaram inteiros. O
sentido não subiu porque mudaram outras coisas, que nenhuma conferência
pega: "PDF" ganhou explicação em 2 páginas, "sujeita o candidato à perda
de direito" virou "perde o direito", e o título "Login Integrado" virou
"Acesso Integrado" (está em 5 páginas, e a IA o troca numa delas a cada
rodada). As duas passagens deram a mesma classe nas 10 páginas. 118.616
tokens de entrada e 51.533 de saída, 252 s.

**Nome e rótulo da tela (1.13.0, 11/10/2026).** O título "Login
Integrado", que aparece em 5 das 10 páginas, virava "Acesso Integrado"
numa delas a cada rodada. A reescrita agora volta à IA quando muda o
texto entre aspas ou o nome de duas ou mais palavras com maiúscula,
inclusive o rótulo solto numa linha. A sigla por extenso dentro do nome
passa, como pede o inciso VIII. Provas antes de medir, sem chave: pega o
"Login Integrado" trocado em todas as rodadas anteriores; o original
contra ele mesmo dá zero acusação em 55 textos; nos curtos, nada. Mesma
regra de decisão da 1.12.0, mesmas 10 páginas, mesmo pedido e mesmo
critério de sentido, com 2 passagens, a 2ª às cegas (semente 20261016;
9 de 10 classes iguais, a divergência resolvida pelo critério).

| Medida | 1.12.0 | 1.13.0 |
|---|---|---|
| Longas: aceitas | 10 / 10 (4 na 2ª tentativa) | 10 / 10 (4 na 2ª tentativa) |
| Longas: apontamentos | 378 → 176 | 378 → 159 |
| Longas: mesmo sentido | 40% (17% a 69%) | **40% (17% a 69%)** |
| Longas com quem faz a ação acrescentado | 4 / 10 | 4 / 10 |
| Longas com outra mudança | 4 / 10 | 3 / 10 |
| Longas com rótulo da tela trocado | 1 / 10 | **0 / 10** |

A conferência ficou. Ela recusou duas tentativas, e as duas tinham
trocado "Login Integrado" por "Acesso Integrado"; a tentativa seguinte
manteve o nome. As outras quatro recusas (incisos piorados, texto de
link, a palavra "EDITOR" que sumiu) também eram mudança real. Escapou
um título de etapa: "Aguardar Análise do IPHAN" virou "Aguardar o
resultado da análise do Instituto do Patrimônio Histórico e Artístico
Nacional (IPHAN)"; a conferência só olha o nome com maiúscula, e ele
ficou. O sentido não subiu: o que mais muda continua sendo a frase que
ganha quem faz a ação ("A autorização deve ser encaminhada" virou "O
solicitante deve encaminhar"), que nenhuma conferência pega. Nenhuma
página mudou só por explicar termo técnico. 143.055 tokens de entrada e
58.561 de saída, 294 s.

**Aspas, nomes e "pode não seguir" no pedido (medida de 22/10/2026, não
entrou).** Duas mudanças só no pedido à IA, medidas juntas: copiar igual
todo texto entre aspas e todo nome com maiúscula, sem sinônimo nem
palavra acrescentada no meio; e a lista de apontamentos passa a dizer o
inciso que cada trecho "pode não seguir", em vez de "descumpre". Regra
escrita antes de rodar: o pedido novo fica se as aceitas não caírem
abaixo de 8 de 10, o mesmo sentido não cair abaixo de 4 de 10 e as
recusas por nome não passarem de 2. Mesmas 10 páginas, achadas de novo
no gov.br (7 com o mesmo texto extraído; 06, 07 e 10 diferem só na
moldura: serviço recomendado e número de avaliações), mesmo critério de
sentido, 2 passagens, a 2ª às cegas (semente 20261021; as 9 classes
iguais).

| Medida | 1.13.0 | Pedido novo |
|---|---|---|
| Longas: aceitas | 10 / 10 | 9 / 10 (a 08 recusada pelo XII) |
| Longas: apontamentos (nas aceitas) | 378 → 159 | 380 → 126 |
| Longas: mesmo sentido | 40% (17% a 69%) | **30% (11% a 60%)** |
| Longas com quem faz a ação acrescentado | 4 / 10 | 5 / 10 |
| Longas com outra mudança | 3 / 10 | 4 / 10 |
| Longas com rótulo da tela trocado | 0 / 10 | 2 / 10 |
| Recusas por nome | 2 | 2 |

O pedido novo não entrou: o mesmo sentido ficou abaixo de 4 de 10, e o
pedido continua o da 1.13.0. A regra das aspas não evitou a troca de
título de etapa ("Aguardar processamento de matrícula" virou "Aguardar o
andamento da matrícula"; a sigla do IPHAN foi por extenso dentro de
"Aguardar Análise do IPHAN"), e o "pode não seguir" não reduziu a frase
que ganha quem faz a ação. Com 10 páginas os intervalos se sobrepõem: a
medida não diz que piorou, só que não melhorou. 235.549 tokens de
entrada e 80.796 de saída (65% mais que na 1.13.0, pelas tentativas a
mais), 403 s.

As 10 páginas, em `https://www.gov.br/pt-br/servicos/` seguido de: 01
`participar-do-programa-crianca-feliz`; 02
`matricular-se-em-curso-de-educacao-superior-de-graduacao-licenciatura-tecnologia-e-bacharelado-ifsp`;
03 `certificado-nacional-de-vacinacao-covid-19`; 04
`devolver-mercadoria-importada-ao-exterior`; 05
`obter-a-aplicacao-prorrogacao-ou-alteracao-de-medida-de-salvaguarda-por-meio-dos-procedimentos-previstos-no-decreto-n-1-488-de-11-de-maio-de-1995`;
06 `obter-duplicacao-de-materiais-filmicos-e-nao-filmicos-da-cinemateca-brasileira`;
07 `revalidar-habilitacao-para-piloto-voo-por-instrumentos-aviao-ifra-ou-helicoptero-ifrh`;
08 `obter-passaporte-comum-para-brasileiro`; 09
`inventariar-linguas-como-referencia-cultural-brasileira-indl`; 10
`autorizar-para-o-exercicio-da-atividade-de-distribuicao-de-gas-natural-comprimido-a-granel-gnc`.
