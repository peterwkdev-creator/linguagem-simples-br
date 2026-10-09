# linguagem-simples-br

Verificador aberto da **Lei 15.263/2025**, a Política Nacional de Linguagem
Simples. Confere um texto contra as 18 técnicas do art. 5º e diz, técnica por
técnica, o que achou, onde achou e o que não confere. Feito para servidor
público, órgão e quem escreve para o cidadão.

> O resultado aponta trechos para revisão. **Não é parecer jurídico** e não
> certifica que um texto cumpre a lei.

> **Em construção.** Ainda não há versão publicada. A precisão medida em
> duas amostras de 30 páginas de serviço do gov.br está em
> [Precisão medida](#precisão-medida), com o método.

## Como usar

Python 3 (testado no 3.12), só a biblioteca padrão, sem instalar nada. Na
pasta do repositório:

```bash
python -m linguagem_simples texto.txt
```

O arquivo é texto, Markdown ou HTML; `-` lê da entrada padrão. HTML é
reconhecido pela extensão (`.html`, `.htm`), pelo começo do arquivo
(`<!doctype html>` ou `<html>`) ou pela opção `--html`. Texto e Markdown em
UTF-8; HTML em UTF-8 ou no charset que a página declara. O
relatório lista os 18 incisos, na ordem da lei, cada um com a classe e o que
aconteceu:

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

| Opção | O que faz |
|---|---|
| `--json` | relatório em JSON, com início, fim, linha e coluna de cada trecho no arquivo lido |
| `--html` | lê como HTML um arquivo que não tem extensão `.html` |
| `--max-palavras N` | inciso II: palavras por frase (padrão 20) |
| `--max-frases N` | inciso III: frases por parágrafo (padrão 8) |
| `--ignorar-sigla SIGLA` | inciso VIII: sigla que o público já conhece (repetível) |
| `--ligar INCISO` | liga um inciso desligado por padrão, como o XI |
| `--desligar INCISO` | desliga um inciso |

Código de saída: 0 sem ocorrências, 1 com ocorrências, 2 erro de uso ou de
leitura.

Também dá para usar como biblioteca:

```python
from linguagem_simples.relatorio import conferir, como_dict

texto = "Procure o INSS. O atendimento é feito de segunda a sexta-feira."
for resultado in conferir(texto):
    for ocorrencia in resultado.ocorrencias:
        print(ocorrencia.inciso, ocorrencia.inicio, ocorrencia.mensagem)
# VIII 10 INSS: primeira ocorrência sem o nome completo antes
# XII 30 voz passiva sem agente: a frase não diz quem faz a ação
```

Para HTML, `ler_html` tira o texto e guarda onde cada trecho está na
página; o relatório recebe a página no lugar do texto e dá linha e coluna
no HTML:

```python
from linguagem_simples.pagina import ler_html
from linguagem_simples.relatorio import conferir, como_texto

pagina = ler_html("<main><p>Procure o <b>INSS</b>.</p></main>")
print(como_texto(conferir(pagina.texto), pagina))
```

Os detectores também se chamam um a um, em `linguagem_simples/detectores.py`.

## O que já confere

| Inciso | Texto da lei | O que o detector aponta | Padrão |
|---|---|---|---|
| II | redigir frases curtas | frase longa | mais de 20 palavras |
| III | desenvolver uma ideia por parágrafo | parágrafo longo, sinal de mais de uma ideia | mais de 8 frases |
| VIII | redigir o nome completo antes das siglas | primeira vez que a sigla aparece sem o nome antes | — |
| XII | redigir frases preferencialmente na voz ativa | verbo "ser" com particípio ("foi entregue pela empresa"), com ou sem quem faz a ação | — |
| XIII | evitar frases intercaladas | trecho entre vírgulas no meio da frase que começa por pronome relativo (", que deve ser apresentado pelo requerente,") | — |
| XIV | evitar o uso de substantivos no lugar de verbos | verbo de apoio com substantivo ("faça a identificação") e substantivo do léxico com complemento ("prevenção da Covid-19") | léxico em `linguagem_simples/lexicos/`, com a fonte de cada palavra |

Os outros 12 incisos aparecem no relatório com a classe de cada um:
**automático** (dá para contar; detector ainda não escrito), **sinal** (dá
para apontar, quem lê decide) ou **fora do alcance** (X e XVIII: só uma
pessoa confere). O inciso XI vem desligado por padrão.

A lei não fixa número. Cada limiar vem de um guia oficial, com a página, em
`linguagem_simples/limiares.py`, e quem usa pode trocar.

## Como cada detector é provado

Para rodar os testes:

```bash
python -m unittest -v
```

Cada detector passa por duas provas: pega o defeito plantado e não dispara
no texto que um guia oficial dá como bom. Onde o guia traz um par "antes e
depois", o "antes" tem de dar mais ocorrências que o "depois". Os trechos
estão em `tests/guias.py`, com a página e o hash do PDF.

**Limites conhecidos:**

- Sigla escrita como nome próprio ("Lacen", "Anvisa") não é reconhecida.
- Com o padrão de 20 palavras, o "depois" da CAPES e o da Anvisa ainda
  têm uma frase acima de 20 (de 21 a 23 palavras); os dois guias aceitam até
  25. Com `--max-palavras 25`, nada aparece.
- XII aponta toda voz passiva com "ser", e a lei diz "preferencialmente":
  o texto que os guias dão como bom também tem passiva sem agente ("podem
  ser utilizadas", TRE-AL; "pode ser punido", Anvisa). A mensagem diz se a
  frase tem ou não quem faz a ação; quem lê decide.
- XII não pega a passiva com "-se" ("recomenda-se"). O par da CAPES
  ("é responsabilidade da CAPES") fica de fora: não tem verbo na passiva.
- XIII só pega o trecho entre vírgulas com pronome relativo; entre
  travessões, não.
- XIV conhece só as palavras que os guias trazem (12, com o plural); fora
  delas, só aponta "fazer" ou "promover" com substantivo em -ção ou -mento.
- XV e XVI ainda sem detector: os guias dão um exemplo de cada, pouco para
  um léxico com fonte.
- HTML: se a página tem `<main>`, só o que está dentro dele conta; sem
  `<main>`, a página inteira, menos menu (`<nav>`), código, formulário e o
  que tem o atributo `hidden`. O CSS não é aplicado: texto escondido por
  CSS entra. Elementos lado a lado sem espaço no HTML colam as palavras
  ("22:24Modificado").
- VIII aponta palavra comum em caixa alta, de ênfase ou de cabeçalho de
  tabela ("OFICIAL", "VALIDADE"): na página do passaporte no gov.br
  (09/10), 6 dos 11 apontamentos do VIII.
- VIII reconhece o nome antes da sigla ligado a ela ("Nome (SIGLA)",
  "Nome - SIGLA", com uma ou mais letras de cada palavra e até duas
  palavras puladas) ou, em qualquer ponto antes, como nome próprio inteiro
  cujas iniciais são a sigla. Fora disso aponta: "Coordenação-Geral de
  Autorização para Transferência Fusão, Cisão, Incorporação e Retirada -
  CGTR" pula quatro palavras do nome. Abreviatura de mês ("31 DEZ")
  também é apontada.

## Precisão medida

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
- II na amostra nova: os 3 erros são título ou link colado à frase seguinte
  sem ponto; um deles é o título da página somado aos "nomes populares" do
  serviço, que o gov.br põe num `<span>` dentro do título.
- XIV aponta substantivo que nomeia uma coisa, não uma ação: documento
  ("Documento de identificação", "Guia de Recolhimento da União") e nome de
  serviço ("Solicitar Análise de Fotoluminescência"). Use o XIV como lista
  para revisar, não como erro certo.
- Nas páginas do gov.br, a lista "Serviços recomendados para você" está
  dentro do `<main>` e entra no texto lido: dos 60 apontamentos do VIII
  anotados, 16 vinham dela.

## Guias usados

Consultados em 09/10/2026:

- TJGO, Guia de Linguagem Simples do TJGO
- CAPES, O uso da Linguagem Simples na CAPES (2026)
- Anvisa, Guia de Linguagem Simples, 1ª edição
- TRE-AL, Linguagem Simples – Cartilha (2024)
- CJF, Guia de Linguagem Simples (2024)
- SES-DF, Guia para simplificar documentos (2024)
- 10 dicas para escrever um documento em Linguagem Simples (repositório da
  Enap)

Texto da lei: publicação original no portal da Câmara dos Deputados, DOU de
17/11/2025.

## Licença

MIT.
