# Precisão medida

Histórico e método das medições de precisão do
[linguagem-simples-br](../README.md). Os números a usar estão na tabela
"Precisão medida" do README; aqui fica cada amostra, na ordem em que foi
medida, com o que mudou entre uma e outra.

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
