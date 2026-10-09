# linguagem-simples-br

Verificador aberto da **Lei 15.263/2025**, a Política Nacional de Linguagem
Simples. Confere um texto contra as 18 técnicas do art. 5º e diz, técnica por
técnica, o que achou, onde achou e o que não confere. Feito para servidor
público, órgão e quem escreve para o cidadão.

> O resultado aponta trechos para revisão. **Não é parecer jurídico** e não
> certifica que um texto cumpre a lei.

> **Em construção.** Ainda não há versão publicada. A precisão de cada
> detector vai aparecer aqui depois de medida, com o método. Hoje não há
> número de precisão.

## Como usar

Python 3 (testado no 3.12), só a biblioteca padrão, sem instalar nada. Na
pasta do repositório:

```bash
python -m linguagem_simples texto.txt
```

O arquivo é texto ou Markdown em UTF-8; `-` lê da entrada padrão. O
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
| `--json` | relatório em JSON, com início, fim, linha e coluna de cada trecho |
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
```

Os detectores também se chamam um a um, em `linguagem_simples/detectores.py`.

## O que já confere

| Inciso | Texto da lei | O que o detector aponta | Padrão |
|---|---|---|---|
| II | redigir frases curtas | frase longa | mais de 20 palavras |
| III | desenvolver uma ideia por parágrafo | parágrafo longo, sinal de mais de uma ideia | mais de 8 frases |
| VIII | redigir o nome completo antes das siglas | primeira vez que a sigla aparece sem o nome antes | — |

Os outros 15 incisos aparecem no relatório com a classe de cada um:
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
- Lê texto e Markdown. HTML ainda não.

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
