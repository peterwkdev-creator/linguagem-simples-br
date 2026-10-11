# Limites conhecidos, inciso por inciso

O que o [linguagem-simples-br](https://github.com/peterwkdev-creator/linguagem-simples-br)
não pega ou pega errado, medido ou visto nas páginas de serviço do gov.br.
Os principais estão no README, em "Limites conhecidos"; os números de
cada medida, em [precisao.md](precisao.md).

## Reescrita por IA

- Foi medida em 28 trechos curtos (de 4 a 68 palavras), tirados de guias
  públicos que o modelo pode ter lido, e em 10 páginas longas do gov.br.
  Nas longas, o sentido mudou em 6 de 10 nas medidas mais recentes.
- O aceite confere números, siglas, links, o texto de cada link, o texto
  entre aspas, o nome escrito com maiúsculas e as alternativas da frase
  de crime ou punição. Não confere as outras condições nem quem faz a
  ação.
- O nome conferido é o de duas ou mais palavras com maiúscula ("Login
  Integrado", "Câmara de Comércio Exterior"). O nome de uma palavra só e o
  que começa a frase não entram. Escrever a sigla por extenso dentro do
  nome ("Análise do Instituto do Patrimônio Histórico e Artístico Nacional
  (IPHAN)") é aceito, como pede o inciso VIII.
- O que se acrescenta em volta do nome passa: o título de etapa
  "Aguardar Análise do IPHAN" virou "Aguardar o resultado da análise do
  Instituto do Patrimônio Histórico e Artístico Nacional (IPHAN)" e foi
  aceito.
- Um texto com ordens dirigidas à IA pode desviar a reescrita, ainda que o
  pedido mande não obedecer: o aceite e a sua leitura são a proteção.

## Siglas (VIII)

- Sigla escrita como nome próprio ("Lacen", "Anvisa") não é reconhecida.
- Deixa de fora a palavra em caixa alta que aparece em minúscula no mesmo
  texto (de cinco letras em diante), o nome de cor ("VERMELHO -
  Emergência"), endereço ("GOV.BR") e o "DE" e o mês da data na epígrafe
  de ato normativo ("RDC Nº 513, DE 27 DE MAIO DE 2021", que a LC 95/1998,
  art. 4º, manda grafar em maiúsculas). Fora disso, palavra comum em caixa
  alta ainda é apontada ("SENHA", "BUSCAR").
- Reconhece o nome antes da sigla ligado a ela ("Nome (SIGLA)", "Nome -
  SIGLA" ou o nome próprio colado, "Nome SIGLA", com uma ou mais letras de
  cada palavra e até duas palavras puladas) ou, em qualquer ponto antes,
  como nome próprio cujas iniciais são a sigla: o nome inteiro ou, se a
  sigla tem três letras ou mais, o fim dele depois de um conectivo
  ("Secretaria Especial da Receita Federal do Brasil" serve a RFB). Com
  duas letras, o fim do nome coincide demais ("Cadastro de Pessoa Física"
  e a PF de Polícia Federal).
- Fora disso aponta: "Coordenação-Geral de Autorização para Transferência
  Fusão, Cisão, Incorporação e Retirada - CGTR" pula quatro palavras do
  nome. Abreviatura de mês ("31 DEZ") também é apontada, e a sigla cujas
  letras não saem das iniciais do nome que vem antes: a sigla em inglês
  ("Serviços de Tráfego Aéreo (ATS)") e a que pega sílabas ("Cadastro de
  Imóveis Rurais (CAFIR)").

## Frase curta (II)

- Com o padrão de 20 palavras, o "depois" da CAPES e o da Anvisa ainda têm
  uma frase acima de 20 (de 21 a 23 palavras); os dois guias aceitam até
  25. Com `--max-palavras 25`, nada aparece.

## Palavra estrangeira (VI)

- É uma lista fechada de 36 entradas, cada uma com a fonte: palavra
  estrangeira fora dela passa (10% de cobertura). "Upload", "courier",
  "desktop", "packing list" e "in loco", que duas leituras às cegas
  mandariam trocar, passam porque nenhum guia oficial lido dá a forma a
  usar no lugar.
- As 12 entradas do TJRS ("performance", "expertise", "in casu", "in
  natura"…) ficaram fora da medida de 96%: nas 520 páginas do gov.br já
  lidas, aparecem em 2, e acertam nas 2.
- Não aponta as que os guias dão como de uso corrente (e-mail, site,
  mouse, download, on-line; "vide", "status" e "data venia", para o Senado
  e o TRF3), nem "menu", que o Senado troca por "cardápio" mas que nas
  páginas de serviço é sempre o menu da tela. Não aponta a palavra dentro
  de endereço ("gov.br/login").
- A sugestão é a do guia e nem sempre cabe: em "login e senha", cabe
  "usuário", não "acesso" (11 dos 25 acertos). Numa página do gov.br lida
  inteira, aponta o título "Login Integrado" do rodapé do portal.

## Lista e tabela (IX)

- Não aponta série de dois itens ("RG e CPF"): com dois, o "e" não separa
  a enumeração de uma frase comum. Os pares da DICAS (p. 2) e da SES-DF
  (p. 6), que põem dois itens em tópicos, passam sem marca.
- Não conta o dois-pontos com menos de 5 palavras antes ("Atenção: leve o
  RG, o CPF e o título"), que nas páginas do gov.br é quase sempre rótulo
  de campo, nem a série que a página já põe em lista ou tabela.
- A série sem dois-pontos ("pague por Pix, cartão ou boleto") também
  passa: é a maioria das enumerações dentro de parágrafo (52 de 59 na
  medida, 7% de cobertura).

## Voz passiva (XII)

- Aponta toda voz passiva com "ser", e a lei diz "preferencialmente": o
  texto que os guias dão como bom também tem passiva sem agente ("podem
  ser utilizadas", TRE-AL; "pode ser punido", Anvisa). A mensagem diz se a
  frase tem ou não quem faz a ação; quem lê decide.
- Não pega a passiva com "-se" ("recomenda-se"). O par da CAPES ("é
  responsabilidade da CAPES") fica de fora: não tem verbo na passiva.

## Frase intercalada (XIII)

- Só pega o trecho entre vírgulas com pronome relativo; entre travessões,
  não. Não sabe onde a oração termina: aponta a oração no fim da frase
  quando ela tem vírgula por dentro (31% de precisão).

## Substantivo no lugar de verbo (XIV)

- Conhece só as palavras que os guias trazem (12, com o plural); fora
  delas, só aponta "fazer" ou "promover" com substantivo em -ção ou
  -mento.
- Não aponta a palavra depois de nome de documento com "de" ("Guia de
  Recolhimento"): o nome do documento não se troca por verbo.

## Redundância (XV)

- Conhece só as expressões que os guias trazem. Nas páginas do gov.br,
  quase tudo o que ele aponta é "de acordo com" (TRE-AL p. 17: prefira
  "segundo, conforme, como"); os pleonasmos da lista ("subir para cima")
  não apareceram. "No Estado de Pernambuco" (CJF) fica de fora: pede a
  lista dos estados.

## Palavra imprecisa (XVI)

- Sem detector, e com a classe **sinal**: nenhum guia oficial dá lista de
  palavras imprecisas. O Manual de Redação da Presidência (2018, p. 17) e
  o Tribunal de Justiça de Minas Gerais (TJMG, p. 6) só dão a regra; a
  CAPES (p. 11), um exemplo ("por descumprimento da norma"); o TJRS
  (p. 58), comandos de despacho ("cumpra-se", "intime-se"). E o mesmo
  Manual usa "oportunamente" num exemplo certo (p. 62), que o TJGO (p. 15)
  reescreve. Se a palavra é imprecisa depende do contexto: quem lê decide.

## Acessibilidade (XVII)

- Lê só a marcação: não vê a imagem, não segue o link e não aplica o CSS.
  Confere três recomendações do eMAG; as outras exigências da Lei
  13.146/2015 que o inciso cita ficam com quem lê. No texto e no Markdown,
  só aponta o link vago (`[clique aqui](url)`).
- Conta como nome do link o texto, o `alt` da imagem dentro dele, o
  `aria-label` e o `aria-labelledby`; o `title` não conta (eMAG 3.5). Link
  sem nome nenhum fica de fora. Imagem com `alt=""`, `aria-hidden="true"`
  ou `role="presentation"` é enfeite e fica de fora; tabela com
  `role="presentation"` também. Tabela de leiaute sem esse `role` é
  apontada: quem lê decide.
- A lista de links vagos é fechada (46 expressões): "Acesse o serviço",
  "Protocolar" ou as abas "O que é?" do modelo do gov.br passam sem marca
  (28% de cobertura).
- Nas páginas do gov.br, o "Saiba mais" do quadro "Login Integrado" do
  portal fica dentro do `<main>` e aparece em quase toda página. Já as
  abas do modelo de página de serviço ("O que é?", "Quem pode utilizar
  este serviço?", "Etapas para a realização deste serviço", "Outras
  Informações") também são vagas pelo eMAG 3.5, mas o XVII não as aponta:
  vêm do portal, não do texto do órgão. Sem marca nelas não quer dizer que
  estão certas.

## Página HTML

- Se a página tem `<main>`, só o que está dentro dele conta; sem `<main>`,
  a página inteira, menos menu (`<nav>`), código, formulário e o que tem o
  atributo `hidden`. O CSS não é aplicado: texto escondido por CSS entra.
  Elementos lado a lado sem espaço no HTML colam as palavras
  ("22:24Modificado").
