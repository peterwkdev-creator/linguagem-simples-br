"""Limiares dos detectores, cada um com a fonte.

A lei não fixa número. Limiar sem fonte de guia oficial não tem padrão:
quem usa informa o valor.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Limiar:
    padrao: object
    fonte: str


LIMIARES = {
    # Frase com mais de 20 palavras é longa. Cinco guias dão 20: TJGO, "Guia
    # de Linguagem Simples do TJGO", p. 9 ("Use no máximo 20 palavras");
    # TRE-AL, "Linguagem Simples – Cartilha" (2024), p. 13; CJF, "Guia de
    # Linguagem Simples" (2024), p. 6; "10 dicas" (repositório da Enap), p. 2;
    # SES-DF (2024), p. 14. Divergem: CAPES (2026), p. 8, dá 25; Anvisa,
    # p. 13, "entre 20 e 25". Consulta: 09/10/2026.
    "II": Limiar(
        20,
        "TJGO p. 9, TRE-AL p. 13, CJF p. 6 e outros dois guias: até 20 "
        "palavras por frase (CAPES dá 25)",
    ),
    # Parágrafo com mais de 8 frases. Único guia com número: TRE-AL,
    # "Linguagem Simples – Cartilha" (2024), p. 14: "não tenha mais que 150
    # palavras e, no máximo, oito frases". Consulta: 09/10/2026.
    "III": Limiar(8, "TRE-AL p. 14: no máximo oito frases por parágrafo"),
}


def valor(inciso, informado=None):
    """O valor informado por quem usa ou, se não houver, o padrão com fonte."""
    if informado is not None:
        return informado
    padrao = LIMIARES[inciso].padrao
    if padrao is None:
        raise ValueError(
            f"inciso {inciso}: limiar sem padrão (nenhum guia oficial com o "
            "número foi conferido); informe o valor"
        )
    return padrao
