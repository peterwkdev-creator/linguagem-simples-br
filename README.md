# linguagem-simples-br

Verificador aberto da **Lei 15.263/2025**, a Política Nacional de Linguagem
Simples. Confere um texto contra as técnicas do art. 5º e diz, técnica por
técnica, o que achou e onde achou. Feito para servidor público, órgão e
quem escreve para o cidadão.

> O resultado aponta trechos para revisão. **Não é parecer jurídico** e não
> certifica que um texto cumpre a lei.

> **Em construção.** Ainda não há versão publicada nem linha de comando. A
> precisão de cada detector vai aparecer aqui depois de medida, com o
> método. Hoje não há número de precisão.

## O que já confere

| Inciso do art. 5º | O que a lei pede | Detector | Padrão |
|---|---|---|---|
| II | usar frases curtas, em ordem direta | `frases_longas` | mais de 20 palavras |
| III | usar parágrafos curtos | `paragrafos_longos` | mais de 8 frases |
| VIII | redigir o nome completo antes das siglas | `siglas_sem_nome` | primeira vez que a sigla aparece |

Os outros 15 incisos estão em `linguagem_simples/incisos.py`, com o texto da
lei e a classe de cada um: **automático** (dá para contar), **sinal** (dá
para apontar, quem lê decide) ou **fora do alcance** (só uma pessoa confere).
O inciso XI vem desligado por padrão.

A lei não fixa número. Cada limiar vem de um guia oficial, com a página, em
`linguagem_simples/limiares.py`, e quem usa pode trocar.

## Como usar

Python 3 (testado no 3.12), só a biblioteca padrão. Na pasta do repositório:

```python
from linguagem_simples.detectores import frases_longas, paragrafos_longos, siglas_sem_nome

texto = "Procure o INSS. O atendimento é feito de segunda a sexta-feira."
for ocorrencia in siglas_sem_nome(texto):
    print(ocorrencia.inciso, ocorrencia.inicio, ocorrencia.mensagem)
# VIII 10 INSS: primeira ocorrência sem o nome completo antes

frases_longas(texto, max_palavras=25)  # limiar informado vence o padrão
```

Cada ocorrência traz o inciso, a posição no texto (`inicio`, `fim`), o
trecho, a mensagem e a medida (palavras ou frases contadas).

Para rodar os testes:

```bash
python -m unittest -v
```

## Como cada detector é provado

Cada detector passa por duas provas: pega o defeito plantado e não dispara
no texto que um guia oficial dá como bom. Onde o guia traz um par "antes e
depois", o "antes" tem de dar mais ocorrências que o "depois". Os trechos
estão em `tests/guias.py`, com a página e o hash do PDF.

**Limites conhecidos:**

- Sigla escrita como nome próprio ("Lacen", "Anvisa") não é reconhecida.
- Com o padrão de 20 palavras, o "depois" da CAPES e o da Anvisa ainda
  têm uma frase de 21 palavras; os dois guias aceitam até 25.

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
