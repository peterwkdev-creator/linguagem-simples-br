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
cole o texto, ou o HTML de uma página, e clique. Não precisa instalar nada,
e o texto não sai do seu computador. Na primeira visita, a página baixa
cerca de 6 MB.

**Precisão medida** em páginas de serviço do gov.br: de cada 100 trechos
que o verificador aponta, uma pessoa confirma de 73 a 100, conforme o
inciso. A exceção é o XIII, que acerta 31% e por isso só aponta trechos
para quem lê decidir. Números por inciso em
[Precisão medida](https://github.com/peterwkdev-creator/linguagem-simples-br#precisão-medida).

> O resultado aponta trechos para revisão. **Não é parecer jurídico** e não
> certifica que um texto cumpre a lei.

## Instalar

### Primeira vez? (Windows)

1. Instale o Python pelo [python.org](https://www.python.org/downloads/).
   Na primeira tela do instalador, marque **Add python.exe to PATH**.
2. Abra o PowerShell: no menu Iniciar, digite "PowerShell".
3. Instale o verificador. Digite o comando abaixo e tecle Enter:
   `python -m pip install linguagem-simples-br`
4. No Bloco de Notas, cole o texto e salve como `carta.txt`. Texto no Word
   ou em PDF: copie e cole no Bloco de Notas.
5. No PowerShell, digite `python -m linguagem_simples ` (com um espaço no
   fim), arraste o arquivo `carta.txt` para a janela e tecle Enter.
6. O relatório aparece na tela: primeiro o resumo, depois os 18 incisos,
   cada trecho com a linha e a coluna onde está. Como ler: em
   [Uso](https://github.com/peterwkdev-creator/linguagem-simples-br#uso).

### Já tem o Python

Python 3.11 ou mais novo; sem outra dependência.

```bash
python -m pip install linguagem-simples-br
```

Ou uma versão exata, direto da tag no GitHub:

```bash
python -m pip install "git+https://github.com/peterwkdev-creator/linguagem-simples-br@v1.13.0"
```

## Uso

```bash
python -m linguagem_simples carta.txt
```

Instalado pelo `pip`, o comando curto `linguagem-simples carta.txt` faz o
mesmo. `linguagem-simples -h` lista as opções, com exemplos.

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

Como ler:

- **Linha e coluna** dizem onde está o trecho: linha 1, coluna 38 é o 38º
  caractere da primeira linha.
- **Automático** é regra que o verificador confere. **Sinal** é indício:
  quem lê decide se muda. **Fora do alcance** é o que só uma pessoa
  confere, como pôr o mais importante primeiro.
- Inciso sem trecho apontado não quer dizer inciso cumprido, sobretudo
  num sinal.

O arquivo pode ser texto (`.txt`), Markdown (`.md`) ou página da internet
(`.html`). Word, PDF e RTF não são lidos: copie o texto para o Bloco de
Notas. Arquivo salvo no padrão antigo do Bloco de Notas (ANSI) é lido com
um aviso.

| Opção | O que faz |
|---|---|
| `--saida ARQUIVO` | grava o relatório num arquivo novo; nunca grava por cima de um que já existe |
| `--max-palavras N` | inciso II: máximo de palavras por frase (padrão 20) |
| `--max-frases N` | inciso III: máximo de frases por parágrafo (padrão 8) |
| `--ignorar-sigla SIGLA` | inciso VIII: sigla que o público já conhece, como CPF (repetível) |
| `--desligar INCISO` | desliga um inciso, como `--desligar XII` |
| `--ligar INCISO` | liga um inciso desligado por padrão: hoje só o XI, que ainda não tem detector e por isso não muda o resultado |
| `--html` | lê como página da internet um arquivo sem a extensão `.html` |
| `--json` | relatório em JSON, para outro programa ler |
| `--reescrever` | pede uma reescrita à IA, com a sua chave ([abaixo](https://github.com/peterwkdev-creator/linguagem-simples-br#reescrita-sugerida-por-ia)) |
| `--versao` | mostra a versão |
| `-h` | mostra a ajuda, com exemplos |

Em Python:

```python
from linguagem_simples.relatorio import conferir

texto = "Procure o INSS para pedir o benefício."
for resultado in conferir(texto):
    for o in resultado.ocorrencias:
        print(resultado.inciso.numero, o.trecho, o.mensagem)
# VIII INSS INSS: primeira ocorrência sem o nome completo antes
```

Mais em
[Para programadores](https://github.com/peterwkdev-creator/linguagem-simples-br#para-programadores).

## Reescrita sugerida por IA

Com `--reescrever`, o Claude, a IA da Anthropic, reescreve o texto a
partir dos apontamentos do relatório, e o verificador confere a reescrita
antes de mostrar:

```bash
python -m linguagem_simples texto.txt --reescrever --saida texto-simples.txt
```

**Leia o texto novo antes de usar.** O verificador confere fatos, links e
nomes, não o sentido. Em página longa, a reescrita mudou o sentido em
mais da metade das páginas medidas (abaixo).

### A chave da API: como funciona

1. **O que é.** A reescrita usa a API da Anthropic, que cobra por uso. A
   chave da API funciona como a senha da sua conta nela, e a biblioteca
   não traz chave nenhuma. Crie a sua em
   [platform.claude.com/settings/keys](https://platform.claude.com/settings/keys);
   o crédito se compra em
   [platform.claude.com/settings/billing](https://platform.claude.com/settings/billing).
2. **O jeito mais simples e mais seguro.** Rode o comando acima no
   PowerShell (no Linux e no macOS, no terminal). Ele pergunta a chave:
   cole e tecle Enter (se o Ctrl+V não colar, use o botão direito do
   mouse). Ela não aparece na tela e vale só para essa vez.
3. **Para não colar toda vez, ou num script**, ponha a chave na variável
   `ANTHROPIC_API_KEY` antes de rodar. Ela vale até fechar o PowerShell,
   mas o comando com a chave fica gravado no histórico dele, em disco: por
   isso o passo 2 é o mais seguro.
   - Windows, PowerShell: `$env:ANTHROPIC_API_KEY = "sua-chave"`
   - Windows, Prompt de Comando: `set ANTHROPIC_API_KEY=sua-chave` (sem aspas)
   - Linux e macOS: `export ANTHROPIC_API_KEY="sua-chave"`
4. **O que a biblioteca faz com ela.** Só a manda para `api.anthropic.com`,
   pela conexão segura (HTTPS), e não segue desvio para outro endereço.
   Não grava em arquivo, não mostra na tela nem no relatório, e nenhuma
   mensagem de erro a mostra. Chave com espaço, quebra de linha ou
   caractere invisível no meio é recusada antes de sair do computador.
5. **Quem paga.** Cada reescrita faz de uma a três chamadas, cobradas na
   conta da chave. A saída diz quantos tokens usou (os pedaços de texto
   que a Anthropic conta para cobrar), também quando para num erro depois
   de uma chamada já paga. O preço está na página de preços da Anthropic.
6. **Para onde vai o texto.** O texto vai para a Anthropic. Antes de
   mandar dado pessoal (Lei Geral de Proteção de Dados, a LGPD) ou
   sigiloso, leia os termos e a política de privacidade dela. A
   [página no navegador](https://peterwkdev-creator.github.io/linguagem-simples-br/)
   não faz reescrita e não manda o texto a ninguém.

Se a chave não for aceita, se faltar crédito, se o modelo não existir ou
se a API estiver fora do ar, a mensagem diz o que fazer.

### Como a reescrita é aceita

- O total de apontamentos cai, e nenhum inciso piora.
- Todo número, data, sigla, link e e-mail do original continua no texto,
  e não aparece número novo.
- O texto de cada link, o texto entre aspas e o nome escrito com
  maiúsculas ("Login Integrado") ficam iguais.
- A frase de crime ou punição não perde nenhuma das alternativas ligadas
  por "ou" ("campos em branco ou informação falsa").

Senão, a IA tenta mais duas vezes, sabendo o que falhou. Se ainda não
passar, a saída diz por que recusou e não mostra o texto; aí você pode
rodar de novo (outra cobrança) ou revisar à mão os trechos do relatório.
Aceita depois de uma recusa, a saída diz o motivo de cada tentativa
recusada.

O texto aceito vai para a tela ou para o arquivo de `--saida`. Se a
gravação falhar, o texto vai para a tela, para não se perder. Numa página
HTML, só o texto é reescrito, sem a marcação. `--modelo` troca o modelo
(padrão `claude-sonnet-5-5`).

### O que se mediu

- **Trecho curto** (28 trechos "antes" de guias oficiais, de 4 a 68
  palavras): todas as reescritas aceitas; o sentido ficou o mesmo em
  **93% (77% a 98%)**.
- **Página longa** (10 páginas de serviço do gov.br com mais de mil
  palavras): todas aceitas; o sentido ficou inteiro em **4 de 10 (17% a
  69%)**. O que mais muda: a reescrita diz quem faz a ação onde o
  original não diz ou troca uma condição por certeza. Nomes e rótulos da
  tela ("Login Integrado") ficaram iguais nas 10.

Em página longa, use a reescrita como rascunho e leia frase por frase. Os
intervalos são de 95%. Cada medida, o método e os erros estão em
[docs/precisao.md](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/docs/precisao.md).

## O que cobre

A lei vale desde 17/11/2025 para a administração direta e indireta de
todos os Poderes e entes (art. 1º), inclusive os municípios. Das 18
técnicas do art. 5º, algumas se contam no texto (frase longa, sigla sem o
nome antes, voz passiva, link "clique aqui"); outras só uma pessoa confere
(o mais importante primeiro, o teste com o público). O verificador aponta
o trecho de cada uma que se conta, diz quais não confere e por quê, e
publica quanto acerta.

| Inciso | Texto da lei | O que o verificador aponta | Padrão |
|---|---|---|---|
| II | redigir frases curtas | frase longa | mais de 20 palavras |
| III | desenvolver uma ideia por parágrafo | parágrafo longo, sinal de mais de uma ideia | mais de 8 frases |
| IV | usar palavras comuns, de fácil compreensão | palavra que um guia oficial manda trocar ("o pedido foi deferido", "dez dias ininterruptos") e a forma que o guia sugere | lista de 86 linhas |
| V | usar sinônimos de termos técnicos e de jargões ou explicá-los no próprio texto | termo técnico que um guia manda trocar ou explicar ("transitou em julgado"), quando o texto não o explica logo depois | lista de 32 termos |
| VI | evitar palavras estrangeiras que não sejam de uso corrente | palavra estrangeira que um guia manda trocar ("faça o login", "um checklist") e a forma que o guia sugere | lista de 36 palavras |
| VIII | redigir o nome completo antes das siglas | primeira vez que a sigla aparece sem o nome antes | — |
| IX | organizar o texto de forma esquemática, quando couber, com o uso de listas, tabelas e recursos gráficos | série de itens dentro do parágrafo, depois dos dois-pontos ("leve os documentos: RG, CPF e comprovante") | 3 itens ou mais |
| XII | redigir frases preferencialmente na voz ativa | verbo "ser" com particípio ("foi entregue pela empresa"), com ou sem quem faz a ação | — |
| XIII | evitar frases intercaladas | trecho entre vírgulas no meio da frase que começa por "que", "o qual" e afins | — |
| XIV | evitar o uso de substantivos no lugar de verbos | "faça a identificação" no lugar de "identifique"; "prevenção da Covid-19" | — |
| XV | evitar redundâncias e palavras desnecessárias | expressão com palavras sobrando ("compareça pessoalmente", "a fim de") e a forma que o guia sugere | lista de 29 expressões |
| XVII | usar linguagem acessível à pessoa com deficiência (Lei 13.146/2015) | link de texto vago ("clique aqui", "saiba mais"); na página HTML, também imagem sem descrição e tabela sem cabeçalho | eMAG 3.1; lista de 46 expressões |

Cada lista fica em `linguagem_simples/lexicos/`, uma entrada por linha,
com o guia e a página de onde veio. A lei não fixa número: cada limiar
também vem de um guia oficial, com a página
(`linguagem_simples/limiares.py`), e quem usa pode trocar. Os guias estão
em [Fontes](https://github.com/peterwkdev-creator/linguagem-simples-br#fontes).

Cada inciso tem uma classe, que o relatório mostra:

- **Automático** (II, III, VIII, XII, XIV e XV): regra que se confere no
  texto. O XI também é automático, mas vem desligado por padrão e ainda
  não tem detector.
- **Sinal** (IV, V, VI, IX, XIII e XVII): o verificador aponta trechos
  para quem lê decidir. O IV, o V e o VI só conhecem as palavras que um
  guia manda trocar, e a palavra difícil depende de quem lê; a lei aceita
  o termo técnico explicado e a palavra estrangeira de uso corrente. O I,
  o VII e o XVI também são sinal, ainda sem detector.
- **Fora do alcance** (X e XVIII): só uma pessoa confere.

## Precisão medida

Dos trechos que o verificador aponta, quantos uma pessoa, lendo o trecho
na página, confirma. Páginas de serviço do gov.br sorteadas, padrões de
fábrica, critério escrito antes de anotar e duas leituras, a segunda às
cegas:

| Inciso | Precisão | Acertos / anotados | Intervalo de 95% | Amostra |
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

O III não apontou nada nas 30 páginas da primeira amostra: sem número. O
V acertou 8 de 8, amostra pequena demais para dar número.

**Precisão não é cobertura.** A tabela diz quanto do que o verificador
aponta está certo, não quanto ele deixa passar. Onde se mediu o que passa,
passa muito: das palavras estrangeiras que duas leituras mandariam
trocar, o VI aponta 10%; dos termos técnicos em notícias do Conselho
Nacional de Justiça, o V aponta 0%; das séries dentro de parágrafo, o IX
aponta 7%. Sem marca não quer dizer sem problema. Cada amostra, o método
e o que os erros mostram estão em
[docs/precisao.md](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/docs/precisao.md).

## Limites conhecidos

Os principais:

- **Não lê o sentido.** Aponta a forma (frase longa, sigla, voz passiva);
  se o texto está claro para o público, só um teste com quem lê diz
  (inciso XVIII).
- **As listas são fechadas.** O IV, o V, o VI, o XIV, o XV e o XVII só
  conhecem as palavras que um guia oficial lista; palavra fora da lista
  passa.
- **O XII aponta toda voz passiva com "ser"**, e a lei diz
  "preferencialmente": a mensagem diz se a frase tem quem faz a ação, e
  quem lê decide.
- **Sigla escrita como nome** ("Anvisa", "Lacen") não é reconhecida.
- **Página HTML:** com `<main>`, só o que está dentro dele conta; o estilo
  da página (CSS) não é aplicado, e texto escondido por ele entra.
- **Reescrita por IA:** confere números, siglas, links, nomes com
  maiúscula, texto entre aspas e as alternativas da frase de punição; não
  confere as outras condições nem quem faz a ação. Um texto com ordens
  dirigidas à IA pode desviar a reescrita: a sua leitura é a proteção.

Todos os limites, inciso por inciso, em
[docs/limites.md](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/docs/limites.md).

## Para programadores

### Linha de comando

- Código de saída: 0 nada a revisar, 1 há trechos a revisar, 2 erro de
  uso ou de leitura. Com `--reescrever`: 0 aceita (ou nada a reescrever),
  1 recusada, 2 erro (sem chave, sem rede ou erro da API). Um defeito do
  próprio verificador também sai com 2, nunca com 1.
- `--json` dá início, fim, linha e coluna de cada trecho no arquivo lido;
  com `--saida`, o JSON vai para o arquivo, e a tela mostra uma linha com
  o resumo. Com `--reescrever --json`, sai o antes e o depois por inciso,
  os tokens e o motivo de cada tentativa recusada (`recusas`).
- `-` no lugar do arquivo lê o texto da entrada padrão. Aí a chave da
  reescrita não é perguntada: use a variável. No Windows PowerShell 5.1,
  passe o arquivo em vez do pipe (`|`): ele troca os acentos por "?" no
  caminho.
- HTML é reconhecido pela extensão (`.html`, `.htm`), pelo começo do
  arquivo (`<!doctype html>` ou `<html>`) ou pela opção `--html`. Texto e
  Markdown em UTF-8; HTML em UTF-8 ou no charset que a página declara.

### Biblioteca

Com a posição de cada trecho:

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

`reescrita.reescrever(texto, chave=...)` faz a reescrita; sem `chave`,
vale a variável `ANTHROPIC_API_KEY`. Os detectores também se chamam um a
um, em `linguagem_simples/detectores.py`.

### Testes

```bash
python -m unittest -v
```

Cada detector passa por duas provas: pega o defeito plantado e não dispara
no texto que um guia oficial dá como bom. Onde o guia traz um par "antes e
depois", o "antes" tem de dar mais ocorrências que o "depois". Os trechos
estão em `tests/guias.py`, com a página e o hash do PDF. Os exemplos em
Python deste README rodam nos testes, como estão.

Para medir de novo a reescrita com a sua chave, da pasta do repositório:
`python docs/medir_reescrita.py medida.jsonl`. Refaz os 28 trechos curtos,
de 28 a 84 chamadas cobradas na sua conta.

### O que há em cada pasta

- `linguagem_simples/`: a biblioteca. `incisos.py` tem os 18 incisos, com
  o texto da lei e a classe de cada um; `texto.py` divide o texto em
  blocos e frases; `pagina.py` lê o HTML; `detectores.py`, um detector por
  inciso; `limiares.py`, os limiares com a fonte; `relatorio.py`, o
  relatório em texto e JSON; `reescrita.py`, a reescrita por IA e o
  aceite dela; `__main__.py`, a linha de comando.
- `linguagem_simples/lexicos/`: as listas, uma entrada por linha, com a
  fonte.
- `tests/`: os testes; `tests/guias.py` traz os trechos dos guias, com a
  página e o hash, e `tests/test_readme.py` roda os exemplos deste README.
- `vitrine/`: a página do "Experimente no navegador". O GitHub Actions a
  monta e publica a cada push que muda a biblioteca, a página ou os testes
  (`.github/workflows/pages.yml`).
- `docs/`: o GIF do começo deste README, o
  [histórico da precisão](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/docs/precisao.md),
  os [limites por inciso](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/docs/limites.md)
  e `medir_reescrita.py`, que refaz a medida da reescrita.
- [`CHANGELOG.md`](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/CHANGELOG.md): o que mudou em cada versão.

## Compatibilidade

Versão semântica. Só mudam numa versão 2: as linhas que o relatório em
texto já tem, os campos do JSON e as opções da linha de comando. Numa 1.x
podem entrar detector novo, linha nova no relatório em texto (como o
resumo e a legenda do topo, na 1.10.0), campo novo no JSON e opção nova.
As mensagens de erro e os avisos da reescrita podem mudar a qualquer
versão. O que mudou em cada versão está no
[CHANGELOG.md](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/CHANGELOG.md).

## Fontes

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
palavra da lista de cores do VIII) e Lei Complementar 95/1998, art. 4º, no
portal do Planalto (epígrafe de ato normativo em maiúsculas).

## Contribuir

Resultado diferente do esperado ou caso que falta?
[Abra uma issue](https://github.com/peterwkdev-creator/linguagem-simples-br/issues/new/choose)
pelo modelo "Resultado diferente do esperado", com texto inventado ou de
página pública, sem dado de pessoa. Para mandar código, veja o
[CONTRIBUTING.md](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/CONTRIBUTING.md); a conversa segue o
[código de conduta](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/CODE_OF_CONDUCT.md).

<!-- outros-projetos:inicio -->
## Outros projetos

| Projeto | Para que serve |
|---|---|
| [numeros-publicos](https://github.com/peterwkdev-creator/numeros-publicos) · [site](https://www.numerospublicos.com.br) | Dados abertos de cada município brasileiro (IBGE, Tesouro Nacional, INEP), conferidos contra a fonte, uma página por município |
| [simples-nacional-br](https://github.com/peterwkdev-creator/simples-nacional-br) · [site](https://peterwkdev-creator.github.io/simples-nacional-br/) | Simples Nacional conferido contra a LC 123 e a LC 214: alíquota, DAS, repartição, Fator R e CNAE |
| [claude-context-cost](https://github.com/peterwkdev-creator/claude-context-cost) · [site](https://peterwkdev-creator.github.io/claude-context-cost/) | Quanto cada fonte (CLAUDE.md, regras, skills, memória) custa no contexto de uma sessão do Claude Code |
| [vra-anac](https://github.com/peterwkdev-creator/vra-anac) | Pontualidade dos voos domésticos do Brasil pelo VRA da ANAC |
| [tts-ptbr](https://github.com/peterwkdev-creator/tts-ptbr) | Voz sintética em português com modelos abertos (Kokoro e Piper), medida pelo Whisper |
| [carrossel-terminal](https://github.com/peterwkdev-creator/carrossel-terminal) | Carrossel do Instagram no visual de terminal: Markdown vira PNG, conferido antes de publicar, e o post vira Reel |
| [ia-testada](https://github.com/peterwkdev-creator/ia-testada) | As medidas por trás dos posts da @peterwk.dev, com o script e como refazer |
| [numerasheets-site](https://github.com/peterwkdev-creator/numerasheets-site) · [site](https://numerasheets.com) | Vitrine da loja NumeraSheets: modelos de planilha e calculadoras grátis |
<!-- outros-projetos:fim -->

## Licença

[MIT](https://github.com/peterwkdev-creator/linguagem-simples-br/blob/main/LICENSE).
