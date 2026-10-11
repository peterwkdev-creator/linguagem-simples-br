# linguagem-simples-br

[![testes](https://github.com/peterwkdev-creator/linguagem-simples-br/actions/workflows/testes.yml/badge.svg)](https://github.com/peterwkdev-creator/linguagem-simples-br/actions/workflows/testes.yml)
[![PyPI](https://img.shields.io/pypi/v/linguagem-simples-br?label=PyPI)](https://pypi.org/project/linguagem-simples-br/)
[![Python](https://img.shields.io/pypi/pyversions/linguagem-simples-br?label=Python)](https://pypi.org/project/linguagem-simples-br/)
[![licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue)](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/LICENSE)

Verificador aberto da **Lei 15.263/2025**, a Política Nacional de Linguagem
Simples. Confere um texto contra os 18 incisos do art. 5º, as técnicas de
escrita que a lei manda usar. Diz, inciso por inciso, o que achou, onde
achou e o que não confere. Feito para servidor público, órgão e quem
escreve para o cidadão.

![Um texto de órgão colado na página; um clique marca a frase longa, a voz passiva e a oração intercalada, e lista os 18 incisos](https://raw.githubusercontent.com/peterwkdev-creator/linguagem-simples-br/main/docs/vitrine.gif)

**[Experimente no navegador](https://peterwkdev-creator.github.io/linguagem-simples-br/)**:
cole o texto, ou o HTML de uma página, e clique. A página roda esta mesma biblioteca no seu
navegador (Pyodide); o texto não sai do seu computador. Na primeira visita
ela baixa cerca de 6 MB e fica pronta em 1,7 s (medido em 10/10/2026, numa
conexão rápida). Depois disso, conferir o texto do exemplo leva uns 5 ms.

**Precisão medida** em páginas de serviço do gov.br, por inciso: XII 100%,
XV 98%, XVII 98%, IV 98%, VI 96%, II 95%, XIV 88%, VIII 78%, IX 73%; o XIII
acerta 31% e por isso só aponta trechos para quem lê decidir. Intervalos em
[Precisão medida](https://github.com/peterwkdev-creator/linguagem-simples-br#precisão-medida).

> O resultado aponta trechos para revisão. **Não é parecer jurídico** e não
> certifica que um texto cumpre a lei.

## Instalar

Python 3.11 ou mais novo; só a biblioteca padrão, sem outra dependência.

```bash
python -m pip install linguagem-simples-br
```

Ou direto da tag no GitHub:

```bash
python -m pip install "git+https://github.com/peterwkdev-creator/linguagem-simples-br@v1.12.0"
```

Sem instalar nada, cole o texto na
[vitrine](https://peterwkdev-creator.github.io/linguagem-simples-br/). Com
o repositório baixado, o comando também roda de dentro da pasta dele, sem
`pip`.

### Primeira vez? (Windows)

1. Instale o Python pelo [python.org](https://www.python.org/downloads/).
   Na primeira tela do instalador, marque **Add python.exe to PATH**.
2. Abra o PowerShell: no menu Iniciar, digite "PowerShell".
3. Instale o verificador: `python -m pip install linguagem-simples-br`.
4. No Bloco de Notas, cole o texto e salve como `carta.txt`, na pasta
   Documentos. Texto no Word ou em PDF: copie e cole no Bloco de Notas.
5. No PowerShell, rode `cd ~\Documents` e depois
   `python -m linguagem_simples carta.txt`.

## Uso

Na linha de comando:

```bash
python -m linguagem_simples carta.txt
```

Com `carta.txt` contendo o texto “Os documentos devem ser entregues no INSS
até sexta-feira.”, o relatório começa assim:

```text
Lei nº 15.263, de 14/11/2025, art. 5º (publicação original, DOU de 17/11/2025, Seção 1, p. 1): relatório dos 18 incisos
O resultado aponta trechos para revisão. Não é parecer jurídico e não certifica que o texto cumpre a lei.

Conferidos nesta versão: II, III, IV, V, VI, VIII, IX, XII, XIII, XIV, XV, XVII. Ocorrências: 2.
Trechos a revisar: 2 (VIII: 1, XII: 1), listados abaixo com linha e coluna.
Classes: automático, regra que o verificador confere; sinal, indício para quem lê decidir; fora do alcance, só uma pessoa confere. Num sinal, nenhuma ocorrência não garante que o inciso foi cumprido.
```

E segue com os 18 incisos, na ordem da lei. Os dois trechos aparecem assim:

```text
VIII. redigir o nome completo antes das siglas
   automático; 1 ocorrência
   - linha 1, coluna 38: INSS: primeira ocorrência sem o nome completo antes: “INSS”
```

```text
XII. redigir frases preferencialmente na voz ativa
   automático; 1 ocorrência
   - linha 1, coluna 21: voz passiva sem agente: a frase não diz quem faz a ação: “ser entregues”
```

Instalado pelo `pip`, o mesmo vale como `linguagem-simples carta.txt`,
com as mesmas opções (`linguagem-simples -h` lista todas, com exemplos).
Para guardar o relatório num arquivo, use `--saida relatorio.txt`.

Em Python:

```python
from linguagem_simples.relatorio import conferir

texto = "Procure o INSS para pedir o benefício."
for resultado in conferir(texto):
    for o in resultado.ocorrencias:
        print(resultado.inciso.numero, o.trecho, o.mensagem)
# VIII INSS INSS: primeira ocorrência sem o nome completo antes
```

O arquivo é texto, Markdown ou HTML; `-` lê da entrada padrão. Word, PDF
e RTF não são lidos: a mensagem pede para copiar o texto para o Bloco de
Notas. Arquivo salvo no padrão antigo do Bloco de Notas (ANSI) é lido com
um aviso. O relatório lista os 18 incisos, na ordem da lei, cada um com a
classe e o que aconteceu. Mais exemplos [abaixo](https://github.com/peterwkdev-creator/linguagem-simples-br#mais-exemplos).

### Reescrita sugerida por IA

Com `--reescrever`, o Claude, a IA da Anthropic, reescreve o texto a
partir dos apontamentos do relatório, e o verificador confere a reescrita
antes de mostrar:

```bash
python -m linguagem_simples texto.txt --reescrever --saida texto-simples.txt
```

#### A chave da API: como funciona

1. **O que é.** A reescrita usa a API da Anthropic, que cobra por uso. A
   chave da API funciona como a senha da sua conta nela, e a biblioteca
   não traz chave nenhuma. Crie a sua em
   [platform.claude.com/settings/keys](https://platform.claude.com/settings/keys);
   o crédito se compra em
   [platform.claude.com/settings/billing](https://platform.claude.com/settings/billing).
2. **O jeito mais simples.** Rode o comando acima no PowerShell (no Linux
   e no macOS, no terminal). Sem chave configurada, ele pergunta: cole a
   chave e tecle Enter (se o Ctrl+V não colar, use o botão direito do
   mouse). Ela não aparece na tela e vale só para essa execução. Com o
   texto pela entrada padrão (`-`), não há pergunta: use o passo 3.
3. **Para não colar toda vez, ou num script**, ponha a chave na variável
   `ANTHROPIC_API_KEY` antes de rodar. A variável vale até fechar o
   PowerShell. Mas o comando com a chave fica gravado no histórico dele,
   em disco, mesmo depois de fechar: por isso o passo 2 é o mais seguro.
   - Windows, PowerShell: `$env:ANTHROPIC_API_KEY = "sua-chave"`
   - Windows, Prompt de Comando: `set ANTHROPIC_API_KEY=sua-chave` (sem aspas)
   - Linux e macOS: `export ANTHROPIC_API_KEY="sua-chave"`
4. **O que a biblioteca faz com ela.** Só a põe no cabeçalho da
   requisição HTTPS para `api.anthropic.com`, sem seguir redirecionamento
   para outro endereço. Não grava em arquivo, não imprime, não põe no
   relatório nem no JSON, e nenhuma mensagem de erro a mostra. Chave com
   espaço, quebra de linha ou caractere invisível no meio é recusada antes
   de sair do computador.
5. **Quem paga.** Cada reescrita faz de uma a três chamadas, cobradas na
   conta da chave. A saída diz quantos tokens usou, de entrada e de saída,
   também quando para num erro depois de uma chamada já paga; o preço por
   token está na página de preços da Anthropic.
6. **Para onde vai o texto.** O texto vai para a Anthropic. Antes de
   mandar dado pessoal (Lei Geral de Proteção de Dados, a LGPD) ou
   sigiloso, leia os termos e a política de
   privacidade dela. A [vitrine](https://peterwkdev-creator.github.io/linguagem-simples-br/)
   não faz reescrita: a página no navegador não leva chave, e o texto
   colado nela não sai do seu computador.

Se a chave não for aceita, se faltar crédito, se o modelo não existir ou
se a API estiver fora do ar, a mensagem diz o que fazer.

#### Como a reescrita é aceita

- O total de apontamentos cai, e nenhum inciso piora.
- Todo número, data, sigla, link e e-mail do original continua no texto,
  e não aparece número novo.
- O texto de cada link fica igual, e a frase de crime ou punição não perde
  nenhuma das alternativas ligadas por "ou" ("campos em branco ou
  informação falsa").

Senão, a IA tenta mais duas vezes, sabendo o que falhou. Se ainda não
passar, a saída diz por que recusou e não mostra o texto. Aceita depois
de uma recusa, a saída diz o motivo de cada tentativa recusada.

O texto aceito vai para a tela ou para o arquivo de `--saida`, que tem de
ser novo: a reescrita nunca grava por cima de um arquivo. Se a gravação
falhar, o texto vai para a tela, para não se perder. Num HTML, só o
texto é reescrito, sem a marcação. `--modelo` troca o modelo (padrão
`claude-sonnet-5-5`). Com `--json`, sai o antes e o depois por inciso, os
tokens e o motivo de cada tentativa recusada (`recusas`). Código de saída: 0 aceita (ou nada a reescrever), 1 recusada,
2 erro (sem chave, sem rede ou erro da API). Recusada, a saída diz o que
fazer: rodar de novo, que é outra cobrança, ou revisar à mão os trechos
do relatório. Em Python,
`reescrita.reescrever(texto, chave=...)` faz o mesmo; sem `chave`, vale a
variável.

O verificador não confere o sentido: compare com o original antes de
usar.

#### O que se mediu

Nos 28 trechos "antes" dos guias oficiais que têm apontamento, as
28 reescritas foram aceitas (41 apontamentos → 1, a sigla DTI, cujo nome
o trecho não dá) e 25 mantiveram o sentido: **89% (73% a 96%)**. Nas
outras 3, a reescrita afirmou que o mandado foi cumprido, escreveu
"Aceitamos" onde o original não diz quem decidiu e trocou "peticionar"
por "entrar com uma ação judicial", a mesma troca que o guia da SES-DF
faz. Na 1.10.1, que desliga o pensamento do modelo, os mesmos 28 deram
**86% (69% a 94%)**, dentro da margem. Na 1.11.0, com o pedido novo
(abaixo), **93% (77% a 98%)**.

**Em página longa, o sentido muda em mais da metade.** Em 10 páginas de
serviço do gov.br com mais de mil palavras, a 1.10.1 não manteve o
sentido inteiro em nenhuma (**0 de 10**): nas 10, dizia quem faz a ação
onde a voz passiva do original não diz ("Os números são atualizados"
virou "O sistema atualiza"), e em 5 mudou algo além disso. A 1.11.0
pede à IA que não faça isso, que não troque possibilidade por certeza,
que não invente o nome de sigla e que não mude o nome de link ou botão.
Nas mesmas 10, as 10 reescritas foram aceitas (378 → 163 apontamentos)
e **4 de 10 (17% a 69%)** mantiveram o sentido. Quem faz a ação ainda
aparece em 4 ("Você fará as correções"); a omissão ainda saiu do crime
numa página que cita o art. 299 do Código Penal; dois nomes de link
mudaram. Nenhum nome de sigla foi inventado, e nenhuma página perdeu
link, e-mail, telefone, prazo ou valor. Sobram mais apontamentos de voz
passiva e de sigla: a reescrita agora os deixa, e quem escreve decide.

A 1.12.0 recusa a reescrita que muda o texto de um link ou que tira uma
alternativa ligada por "ou" de uma frase de crime ou punição. Nas mesmas
10 páginas, as 10 foram aceitas, 4 depois de uma recusa (378 → 176
apontamentos). O crime e os links ficaram inteiros, e o sentido ficou em
**4 de 10 (17% a 69%)** de novo, porque mudaram outras coisas: "PDF"
ganhou uma explicação, "sujeita à perda do direito" virou "perde o
direito", e "Login Integrado", que é título e não link, virou "Acesso
Integrado".
Em página longa, use a reescrita como rascunho e leia frase por frase.

Método em [docs/precisao.md](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/docs/precisao.md); para medir de novo
com a sua chave, `python docs/medir_reescrita.py medida.jsonl`.

## Por quê

A Lei 15.263/2025 vale desde 17/11/2025 para a administração direta e
indireta de todos os Poderes e entes (art. 1º), inclusive os municípios. O
art. 5º lista, em 18 incisos, as técnicas de escrita. Algumas se contam no texto (frase
longa, sigla sem o nome antes, voz passiva, link "clique aqui"); outras só
uma pessoa confere (o mais importante primeiro, o teste com o público).

Este verificador aponta o trecho de cada uma que se conta, diz quais não
confere e por quê, e publica quanto acerta, medido em páginas reais de
órgão. Cada limiar e cada palavra dos léxicos vem de um guia oficial, com
a página.

## O que cobre

| Inciso | Texto da lei | O que o detector aponta | Padrão |
|---|---|---|---|
| II | redigir frases curtas | frase longa | mais de 20 palavras |
| III | desenvolver uma ideia por parágrafo | parágrafo longo, sinal de mais de uma ideia | mais de 8 frases |
| IV | usar palavras comuns, de fácil compreensão | palavra que um guia oficial manda trocar por outra mais conhecida ("o pedido foi deferido", "dez dias ininterruptos") e a forma que o guia sugere | léxico em `linguagem_simples/lexicos/palavras-complexas.txt`: 86 linhas do TJRS, da CAPES, da Anvisa e da SES-DF, com as formas do verbo |
| V | usar sinônimos de termos técnicos e de jargões ou explicá-los no próprio texto | termo técnico ou jargão que um guia manda trocar ou explicar ("exordial acusatória", "transitou em julgado"), quando o texto não o explica logo depois (entre parênteses, com "ou seja" ou "isto é") | léxico em `linguagem_simples/lexicos/jargoes.txt`: 32 entradas do TJRS, da SES-DF e da Anvisa |
| VI | evitar palavras estrangeiras que não sejam de uso corrente | palavra estrangeira que um guia oficial manda trocar ("faça o login", "um checklist") e a forma que o guia sugere | léxico em `linguagem_simples/lexicos/estrangeirismos.txt`: 36 entradas da CAPES, da Anvisa, do TJGO, do TJRS e do Manual de Comunicação do Senado |
| VIII | redigir o nome completo antes das siglas | primeira vez que a sigla aparece sem o nome antes | — (nome de cor em caixa alta, como "VERMELHO", não conta como sigla: lista em `linguagem_simples/lexicos/cores.txt`, com a fonte de cada palavra) |
| IX | organizar o texto de forma esquemática, quando couber, com o uso de listas, tabelas e recursos gráficos | frase de parágrafo que anuncia uma série depois dos dois-pontos, com os itens separados por vírgula ou ponto e vírgula ("leve ao atendimento os documentos: RG, CPF e comprovante") | 3 itens ou mais |
| XII | redigir frases preferencialmente na voz ativa | verbo "ser" com particípio ("foi entregue pela empresa"), com ou sem quem faz a ação | — |
| XIII | evitar frases intercaladas | trecho entre vírgulas no meio da frase que começa por pronome relativo (", que deve ser apresentado pelo requerente,") | — |
| XIV | evitar o uso de substantivos no lugar de verbos | verbo de apoio com substantivo ("faça a identificação") e substantivo do léxico com complemento ("prevenção da Covid-19") | léxico em `linguagem_simples/lexicos/`, com a fonte de cada palavra |
| XV | evitar redundâncias e palavras desnecessárias | expressão do léxico com palavras sobrando ("compareça pessoalmente", "a fim de", "de acordo com") e a forma que o guia sugere | léxico em `linguagem_simples/lexicos/redundancias.txt`: 29 entradas do TRE-AL, do CJF e da CAPES, com a página |
| XVII | usar linguagem acessível à pessoa com deficiência (Lei 13.146/2015) | no HTML, link de texto vago ("clique aqui", "saiba mais"), imagem sem `alt` e tabela sem célula de cabeçalho (`th`); no texto e no Markdown, só o link vago | eMAG 3.1, recomendações 3.5, 3.6 e 3.10; léxico em `linguagem_simples/lexicos/links-vagos.txt`: 46 entradas |

As siglas dos guias (TJRS, CAPES e outras) estão por extenso em
[Guias usados](https://github.com/peterwkdev-creator/linguagem-simples-br#guias-usados).

Cada inciso tem uma classe, que o relatório mostra:

- **Automático** (II, III, VIII, XII, XIV e XV): regra que se confere no
  texto. O XI também é automático, mas vem desligado por padrão e ainda
  não tem detector.
- **Sinal** (IV, V, VI, IX, XIII e XVII): o detector aponta trechos para
  quem lê decidir. O IV, o V e o VI só conhecem as palavras que um guia
  manda trocar, e a palavra difícil depende de quem lê (TJRS, p. 31); a
  lei aceita o termo técnico explicado e a palavra estrangeira de uso
  corrente. O IX acerta 73%, e a lei diz "quando couber"; o XIII acerta
  31%; o XVII confere só três pontos do que a Lei 13.146/2015 pede. O I,
  o VII e o XVI também são sinal, ainda sem detector.
- **Fora do alcance** (X e XVIII): só uma pessoa confere.

Num sinal, "nenhuma ocorrência" não garante que o texto cumpre o inciso.

A lei não fixa número. Cada limiar vem de um guia oficial, com a página, em
`linguagem_simples/limiares.py`, e quem usa pode trocar.

## Como é testado

Para rodar os testes:

```bash
python -m unittest -v
```

Cada detector passa por duas provas: pega o defeito plantado e não dispara
no texto que um guia oficial dá como bom. Onde o guia traz um par "antes e
depois", o "antes" tem de dar mais ocorrências que o "depois". Os trechos
estão em `tests/guias.py`, com a página e o hash do PDF. Os exemplos em
Python deste README rodam nos testes, como estão.

### Precisão medida

Dos trechos que cada detector aponta, quantos uma pessoa, lendo o trecho na
página, confirma. Páginas de serviço do gov.br sorteadas, padrões de
fábrica, critério escrito antes de anotar e duas passagens, a segunda às
cegas:

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% (Wilson) | Amostra |
|---|---|---|---|---|
| XII | 100% | 59 / 59 | 94% a 100% | 30 páginas, 09/10/2026 |
| XV | 98% | 59 / 60 | 91% a 100% | 150 páginas, 10/10/2026 |
| XVII | 98% | 49 / 50 | 90% a 100% | 150 páginas, 10/10/2026 |
| IV | 98% | 40 / 41 | 87% a 100% | 490 páginas, 11/10/2026 |
| VI | 96% | 25 / 26 | 81% a 99% | 120 páginas novas, 10/10/2026 |
| II | 95% | 57 / 60 | 86% a 98% | 30 páginas, 09/10/2026 |
| XIV | 88% | 21 / 24 | 69% a 96% | 30 páginas, 09/10/2026 |
| VIII | 78% | 38 / 49 | 64% a 87% | 30 páginas, 09/10/2026 |
| IX | 73% | 22 / 30 | 56% a 86% | 220 páginas novas, 10/10/2026 |
| XIII | 31% | 13 / 42 | 19% a 46% | 150 páginas, 09/10/2026 |

III não apontou nada nas 30 páginas da primeira amostra: sem número.
Precisão não é cobertura: o que o detector deixa passar não entra nesta
conta. Do XVII, a cobertura também foi medida: em 30 páginas novas, dos
18 nomes de link vagos, ele aponta 5 (**28%**, de 12% a 51%), sem apontar
nenhum nome que diz o destino. O léxico dele é uma lista fechada (46
expressões na 1.2.0): "Acesse o serviço", "Protocolar" ou as abas "O que
é?" do modelo do gov.br passam sem marca. O IX foi medido duas vezes: a
1ª versão acertou 43% nas 180 páginas das outras amostras, quase sempre
errando no dois-pontos de rótulo ("Atenção:", "Endereço:"); a 1.3.0 não
conta esse dois-pontos, e o número acima é dela, em páginas que nenhuma
versão tinha visto. A cobertura do IX é baixa por desenho: das 59
enumerações dentro de parágrafo numa amostra de 150 frases com série
("Pix, cartão de crédito ou boleto"), ele aponta 4 (**7%**, de 3% a 16%),
porque 52 delas não têm dois-pontos. Sem marca do IX não quer dizer sem
enumeração. O VI erra pouco e deixa passar muito: o único erro foi "login
único", nome de serviço; mas, das 20 palavras estrangeiras que duas
passagens às cegas mandariam trocar em 30 páginas novas ("courier",
"upload", "in loco", "vide"), ele aponta 2 (**10%**, de 3% a 30%), porque
só conhece as que um guia lista. E quase tudo o que ele aponta é "login"
(96 de 103 nas 120 páginas), que a CAPES manda trocar por "acesso", mas
que as mesmas passagens deram como de uso corrente: quem lê decide.
O IV aponta a palavra que um guia manda trocar ("protocolar",
"requerer", "deferimento"): o único erro foi o nome de uma opção da tela
entre aspas; em 5 dos 40 acertos, a forma do guia não cabe ("a licença
será expedida": cabe "emitida", não "enviada"), e a mensagem diz o que o
guia sugere, não o que serve no trecho. O V acerta onde aponta (8 de 8
em páginas de serviço, **amostra pequena**), mas a lista dos guias é
estreita: em 120 notícias do Conselho Nacional de Justiça (CNJ) ele apontou uma vez, e dos 77 termos
técnicos que duas passagens às cegas listaram em 30 delas ("autos",
"liminar", "mérito", "precatórios"), não apontou nenhum (**0%**, de 0% a
5%). Sem marca do V não quer dizer sem jargão. Cada
amostra, o método e o que os erros mostram estão em
[docs/precisao.md](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/docs/precisao.md).

## Mais exemplos

O relatório em texto, com a linha e a coluna de cada trecho:

```text
II. redigir frases curtas
   automático; limiar 20, fonte: TJGO p. 9, TRE-AL p. 13, CJF p. 6 e outros dois guias: até 20 palavras por frase (CAPES dá 25); 1 ocorrência
   - linha 1, coluna 1: frase com 27 palavras (limiar: 20): “Certifico e dou fé que, dando cumprimento ao mandado subscrito extraí…”

VIII. redigir o nome completo antes das siglas
   automático; 1 ocorrência
   - linha 3, coluna 21: INSS: primeira ocorrência sem o nome completo antes: “INSS”

X. organizar o texto a fim de que as informações mais importantes apareçam primeiramente
   fora do alcance; não conferido: só uma pessoa confere
```

HTML é reconhecido pela extensão (`.html`, `.htm`), pelo começo do arquivo
(`<!doctype html>` ou `<html>`) ou pela opção `--html`. Texto e Markdown em
UTF-8; HTML em UTF-8 ou no charset que a página declara.

| Opção | O que faz |
|---|---|
| `--json` | relatório em JSON, com início, fim, linha e coluna de cada trecho no arquivo lido |
| `--html` | lê como HTML um arquivo que não tem extensão `.html` |
| `--max-palavras N` | inciso II: palavras por frase (padrão 20) |
| `--max-frases N` | inciso III: frases por parágrafo (padrão 8) |
| `--ignorar-sigla SIGLA` | inciso VIII: sigla que o público já conhece, como CPF (repetível) |
| `--ligar INCISO` | liga um inciso desligado por padrão: hoje só o XI, que ainda não tem detector |
| `--desligar INCISO` | desliga um inciso, como `--desligar XII` |
| `--saida ARQUIVO` | grava o relatório (ou, com `--reescrever`, o texto aceito) num arquivo novo, nunca por cima de um que já existe |
| `--reescrever` | pede uma reescrita à IA, com a sua chave da API ([acima](https://github.com/peterwkdev-creator/linguagem-simples-br#reescrita-sugerida-por-ia)) |
| `--versao` | mostra a versão |
| `-h` | mostra a ajuda, com exemplos |

### Para quem automatiza

- Código de saída: 0 nada a revisar, 1 há trechos a revisar, 2 erro de
  uso ou de leitura. Com `--reescrever`: 0 aceita (ou nada a reescrever),
  1 recusada, 2 erro. Um defeito do próprio verificador também sai com 2,
  nunca com 1.
- `--json` dá início, fim, linha e coluna de cada trecho no arquivo lido;
  com `--saida`, o JSON vai para o arquivo, e a tela mostra uma linha com
  o resumo.
- `-` lê o texto da entrada padrão. No Windows PowerShell 5.1, passe o
  arquivo em vez do pipe (`|`): ele troca os acentos por "?" no caminho.
- O que muda entre versões está em
  [Compatibilidade](https://github.com/peterwkdev-creator/linguagem-simples-br#compatibilidade).

Também dá para usar como biblioteca, com a posição de cada trecho:

```python
from linguagem_simples.relatorio import conferir, como_dict

texto = "Procure o INSS. O atendimento é feito de segunda a sexta-feira."
for resultado in conferir(texto):
    for ocorrencia in resultado.ocorrencias:
        print(ocorrencia.inciso, ocorrencia.inicio, ocorrencia.mensagem)
# VIII 10 INSS: primeira ocorrência sem o nome completo antes
# XII 30 voz passiva sem agente: a frase não diz quem faz a ação
```

Para HTML, `ler_html` tira o texto e guarda onde cada trecho e cada link,
imagem e tabela estão na página; o relatório recebe a página no lugar do
texto, confere também o XVII e dá linha e coluna no HTML:

```python
from linguagem_simples.pagina import ler_html
from linguagem_simples.relatorio import conferir, como_texto

pagina = ler_html('<main><p>Para pedir, <a href="/pedir">clique aqui</a>.</p></main>')
for resultado in conferir(pagina):
    for o in resultado.ocorrencias:
        print(o.inciso, o.trecho, o.mensagem)
# XVII clique aqui link com texto que não diz o destino (eMAG 3.5)
print(como_texto(conferir(pagina), pagina))
```

Os detectores também se chamam um a um, em `linguagem_simples/detectores.py`.

## Fontes e limites

### Guias usados

Consultados em 09/10/2026:

- Tribunal de Justiça do Estado de Goiás (TJGO), Guia de Linguagem
  Simples do TJGO
- Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES), O
  uso da Linguagem Simples na CAPES (2026)
- Agência Nacional de Vigilância Sanitária (Anvisa), Guia de Linguagem
  Simples, 1ª edição
- Tribunal Regional Eleitoral de Alagoas (TRE-AL), Linguagem Simples –
  Cartilha (2024)
- Conselho da Justiça Federal (CJF), Guia de Linguagem Simples (2024)
- Secretaria de Estado de Saúde do Distrito Federal (SES-DF), Guia para
  simplificar documentos (2024)
- 10 dicas para escrever um documento em Linguagem Simples (DICAS, no
  repositório da Escola Nacional de Administração Pública, a Enap)

Consultados em 10/10/2026:

- eMAG, Modelo de Acessibilidade em Governo Eletrônico, versão 3.1
  (obrigatório no governo federal pela Portaria nº 3, de 07/05/2007, da
  Secretaria de Logística e Tecnologia da Informação), recomendações 3.5,
  3.6 e 3.10
- Senado Federal, Manual de Comunicação: verbete "Estrangeirismo" (pares
  do VI e a lista de palavras de uso amplo, que o VI não aponta) e a lista
  "Estrangeirismos grafados sem itálico ou aspas"
- Tribunal de Justiça do Rio Grande do Sul (TJRS), Guia de Linguagem
  Simples (2022): quadro de palavras complexas (p. 31 e 32, IV), exemplos
  de jargões e termos técnicos (p. 34), quadro "Expressões que devem ser
  evitadas" (p. 107, V) e quadro de expressões estrangeiras (p. 36)
- Tribunal Regional Federal da 3ª Região (TRF3), Escola de Magistrados,
  "Expressões latinas em textos jurídicos" (2021)

Texto da lei: publicação original no portal da Câmara dos Deputados, DOU de
17/11/2025.

Outras fontes: Dicionário Priberam da Língua Portuguesa (um verbete por
palavra do léxico de cores) e Lei Complementar 95/1998, art. 4º, no portal
do Planalto (epígrafe de ato normativo em maiúsculas).

### Limites conhecidos

- A reescrita por IA foi medida em 28 trechos curtos (de 4 a 68
  palavras), tirados de guias públicos que o modelo pode ter lido, e em
  10 páginas longas do gov.br; nas longas, o sentido mudou em 6 de 10
  nas duas últimas medidas (ver "O que se mediu"). O aceite confere
  números, siglas, links, o texto de cada link e as alternativas da frase
  de crime ou punição; não confere nomes, as outras condições nem quem
  faz a ação. Um texto com ordens
  dirigidas à IA pode desviar a reescrita, ainda que o pedido mande não
  obedecer: o aceite e a sua leitura são a proteção.

- Sigla escrita como nome próprio ("Lacen", "Anvisa") não é reconhecida.
- Com o padrão de 20 palavras, o "depois" da CAPES e o da Anvisa ainda
  têm uma frase acima de 20 (de 21 a 23 palavras); os dois guias aceitam até
  25. Com `--max-palavras 25`, nada aparece.
- VI é uma lista fechada de 36 entradas, cada uma com a fonte: palavra
  estrangeira fora dela passa (10% de cobertura, acima). "Upload",
  "courier", "desktop", "packing list" e "in loco", que as passagens
  mandariam trocar, passam porque nenhum guia oficial lido dá a forma a
  usar no lugar. As 12 entradas do TJRS (1.5.0: "performance",
  "expertise", "in casu", "in natura"…) ficaram fora da medida de 96%:
  nas 520 páginas do gov.br já lidas, aparecem em 2, e acertam nas 2.
  Não aponta as que os guias dão como de uso corrente (e-mail, site,
  mouse, download, on-line; "vide", "status" e "data venia", para o
  Senado e o TRF3), nem "menu", que o Senado troca por "cardápio" mas que nas
  páginas de serviço é sempre o menu da tela. Não aponta a palavra dentro
  de endereço ("gov.br/login"). A sugestão é a do guia e nem sempre cabe:
  em "login e senha", cabe "usuário", não "acesso" (11 dos 25 acertos).
  Numa página do gov.br lida inteira, aponta o título "Login Integrado"
  do rodapé do portal.
- IX não aponta série de dois itens ("RG e CPF"): com dois, o "e" não
  separa a enumeração de uma frase comum. Os pares da DICAS (p. 2) e da
  SES-DF (p. 6), que põem dois itens em tópicos, passam sem marca. Também
  não conta o dois-pontos com menos de 5 palavras antes ("Atenção: leve o
  RG, o CPF e o título"), que nas páginas do gov.br é quase sempre rótulo
  de campo, nem a série que a página já põe em lista ou tabela. A série
  sem dois-pontos ("pague por Pix, cartão ou boleto") também passa: é a
  maioria das enumerações dentro de parágrafo (52 de 59 na medida).
- XII aponta toda voz passiva com "ser", e a lei diz "preferencialmente":
  o texto que os guias dão como bom também tem passiva sem agente ("podem
  ser utilizadas", TRE-AL; "pode ser punido", Anvisa). A mensagem diz se a
  frase tem ou não quem faz a ação; quem lê decide.
- XII não pega a passiva com "-se" ("recomenda-se"). O par da CAPES
  ("é responsabilidade da CAPES") fica de fora: não tem verbo na passiva.
- XIII só pega o trecho entre vírgulas com pronome relativo; entre
  travessões, não. Não sabe onde a oração termina: aponta a oração no fim
  da frase quando ela tem vírgula por dentro (31% de precisão, acima).
- XIV conhece só as palavras que os guias trazem (12, com o plural); fora
  delas, só aponta "fazer" ou "promover" com substantivo em -ção ou -mento.
- XV conhece só as expressões que os guias trazem. Nas páginas do gov.br,
  quase tudo o que ele aponta é "de acordo com" (TRE-AL p. 17: prefira
  "segundo, conforme, como"); os pleonasmos da lista ("subir para cima")
  não apareceram. "No Estado de Pernambuco" (CJF) fica de fora: pede a
  lista dos estados.
  Não aponta a palavra depois de nome de documento com "de" ("Guia de
  Recolhimento"): o nome do documento não se troca por verbo.
- XVI sem detector, e com a classe **sinal**: nenhum guia
  oficial dá lista de palavras imprecisas. O Manual de Redação da
  Presidência (2018, p. 17) e o Tribunal de Justiça de Minas Gerais (TJMG, p. 6) só dão a regra; a CAPES
  (p. 11), um exemplo ("por descumprimento da norma"); o TJRS (p. 58),
  comandos de despacho ("cumpra-se", "intime-se"). E o mesmo Manual usa
  "oportunamente" num exemplo certo (p. 62), que o TJGO (p. 15) reescreve.
  Se a palavra é imprecisa depende do contexto: quem lê decide.
- XVII lê só a marcação: não vê a imagem, não segue o link e não aplica o
  CSS. Confere três recomendações do eMAG; as outras exigências da Lei
  13.146/2015 que o inciso cita ficam com quem lê. No texto e no Markdown,
  só aponta o link vago (`[clique aqui](url)`).
- XVII conta como nome do link o texto, o `alt` da imagem dentro dele, o
  `aria-label` e o `aria-labelledby`; o `title` não conta (eMAG 3.5). Link
  sem nome nenhum fica de fora. Imagem com `alt=""`, `aria-hidden="true"`
  ou `role="presentation"` é enfeite e fica de fora; tabela com
  `role="presentation"` também. Tabela de leiaute sem esse `role` é
  apontada: quem lê decide.
- XVII nas páginas do gov.br: o "Saiba mais" do quadro "Login Integrado"
  do portal fica dentro do `<main>` e aparece em quase toda página. Já as
  abas do modelo de página de serviço ("O que é?", "Quem pode utilizar
  este serviço?", "Etapas para a realização deste serviço", "Outras
  Informações") também são vagas pelo eMAG 3.5, mas o XVII não as aponta:
  vêm do portal, não do texto do órgão. Sem marca nelas não quer dizer
  que estão certas.
- HTML: se a página tem `<main>`, só o que está dentro dele conta; sem
  `<main>`, a página inteira, menos menu (`<nav>`), código, formulário e o
  que tem o atributo `hidden`. O CSS não é aplicado: texto escondido por
  CSS entra. Elementos lado a lado sem espaço no HTML colam as palavras
  ("22:24Modificado").
- VIII deixa de fora a palavra em caixa alta que aparece em minúscula no
  mesmo texto (de cinco letras em diante), o nome de cor ("VERMELHO -
  Emergência"), endereço ("GOV.BR") e o "DE" e o mês da data na epígrafe
  de ato normativo ("RDC Nº 513, DE 27 DE MAIO DE 2021", que a LC 95/1998,
  art. 4º, manda grafar em maiúsculas). Fora disso, palavra comum em caixa
  alta ainda é apontada ("SENHA", "BUSCAR").
- VIII reconhece o nome antes da sigla ligado a ela ("Nome (SIGLA)",
  "Nome - SIGLA" ou o nome próprio colado, "Nome SIGLA", com uma ou mais
  letras de cada palavra e até duas palavras puladas) ou, em qualquer
  ponto antes, como nome próprio cujas iniciais são a sigla: o nome
  inteiro ou, se a sigla tem três letras ou mais, o fim dele depois de um
  conectivo ("Secretaria Especial da Receita Federal do Brasil" serve a
  RFB). Com duas letras, o fim do nome coincide demais ("Cadastro de
  Pessoa Física" e a PF de Polícia Federal). Fora disso aponta:
  "Coordenação-Geral de Autorização para Transferência Fusão, Cisão,
  Incorporação e Retirada - CGTR" pula quatro palavras do nome. Abreviatura de mês ("31 DEZ")
  também é apontada, e a sigla cujas letras não saem das iniciais do nome
  que vem antes: a sigla em inglês ("Serviços de Tráfego Aéreo (ATS)") e a
  que pega sílabas ("Cadastro de Imóveis Rurais (CAFIR)").

## O que há em cada pasta

- `linguagem_simples/`: a biblioteca. `incisos.py` tem os 18 incisos, com
  o texto da lei e a classe de cada um; `texto.py` divide o texto em
  blocos e frases; `pagina.py` lê o HTML; `detectores.py`, um detector por
  inciso; `limiares.py`, os limiares com a fonte; `relatorio.py`, o
  relatório em texto e JSON; `reescrita.py`, a reescrita por IA e o
  aceite dela; `__main__.py`, a linha de comando.
- `linguagem_simples/lexicos/`: os léxicos, uma entrada por linha, com a
  fonte.
- `tests/`: os testes; `tests/guias.py` traz os trechos dos guias, com a
  página e o hash, e `tests/test_readme.py` roda os exemplos deste README.
- `vitrine/`: a página do "Experimente no navegador". O GitHub Actions a
  monta e publica a cada push que muda a biblioteca, a página ou os testes
  (`.github/workflows/pages.yml`).
- `docs/`: o GIF do começo deste README, o
  [histórico da precisão](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/docs/precisao.md) e `medir_reescrita.py`, que
  refaz a medida da reescrita.
- [`CHANGELOG.md`](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/CHANGELOG.md): o que mudou em cada versão.

## Compatibilidade

Versão semântica. Só mudam numa versão 2: as linhas que o relatório em
texto já tem, os campos do JSON e as opções da linha de comando. Numa 1.x
podem entrar detector novo, linha nova no relatório em texto (como o
resumo e a legenda do topo, na 1.10.0), campo novo no JSON e opção nova.
As mensagens de erro podem mudar a qualquer versão. O que
mudou em cada versão está no [CHANGELOG.md](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/CHANGELOG.md).

## Contribuir

Resultado diferente do esperado ou caso que falta?
[Abra uma issue](https://github.com/peterwkdev-creator/linguagem-simples-br/issues/new/choose)
pelo modelo "Resultado diferente do esperado", com texto inventado ou de
página pública, sem dado de pessoa. Para mandar código, veja o
[CONTRIBUTING.md](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/CONTRIBUTING.md); a conversa segue o
[código de conduta](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/CODE_OF_CONDUCT.md).

## Licença

[MIT](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/LICENSE).
