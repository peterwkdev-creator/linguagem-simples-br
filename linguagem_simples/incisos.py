"""Os 18 incisos do art. 5º da Lei 15.263/2025 e a classe de cada um.

Texto da publicação original (Câmara, Legislação Informatizada, DOU de
17/11/2025, Seção 1, p. 1), conferido em 09/10/2026 contra o HTML da página.
A lei não fixa número para nenhuma técnica: os limiares estão em
``limiares.py``, cada um com a fonte.
"""

from dataclasses import dataclass

FONTE_LEI = (
    "Lei nº 15.263, de 14/11/2025, art. 5º (publicação original, "
    "DOU de 17/11/2025, Seção 1, p. 1)"
)

AUTOMATICO = "automático"
SINAL = "sinal"
FORA_DO_ALCANCE = "fora do alcance"


@dataclass(frozen=True)
class Inciso:
    numero: str
    texto: str
    classe: str
    ligado_por_padrao: bool = True


INCISOS = (
    Inciso("I", "redigir frases em ordem direta", SINAL),
    Inciso("II", "redigir frases curtas", AUTOMATICO),
    Inciso("III", "desenvolver uma ideia por parágrafo", AUTOMATICO),
    Inciso("IV", "usar palavras comuns, de fácil compreensão", SINAL),
    Inciso(
        "V",
        "usar sinônimos de termos técnicos e de jargões ou explicá-los no "
        "próprio texto",
        SINAL,
    ),
    Inciso("VI", "evitar palavras estrangeiras que não sejam de uso corrente", SINAL),
    Inciso("VII", "não usar termos pejorativos", SINAL),
    Inciso("VIII", "redigir o nome completo antes das siglas", AUTOMATICO),
    Inciso(
        "IX",
        "organizar o texto de forma esquemática, quando couber, com o uso de "
        "listas, tabelas e recursos gráficos",
        SINAL,
    ),
    Inciso(
        "X",
        "organizar o texto a fim de que as informações mais importantes "
        "apareçam primeiramente",
        FORA_DO_ALCANCE,
    ),
    Inciso(
        "XI",
        "não usar novas formas de flexão de gênero e de número das palavras "
        "da língua portuguesa, em contrariedade às regras gramaticais "
        "consolidadas, ao Vocabulário Ortográfico da Língua Portuguesa (Volp) "
        "e ao Acordo Ortográfico da Língua Portuguesa, promulgado pelo "
        "Decreto nº 6.583, de 29 de setembro de 2008",
        AUTOMATICO,
        ligado_por_padrao=False,
    ),
    Inciso("XII", "redigir frases preferencialmente na voz ativa", AUTOMATICO),
    Inciso("XIII", "evitar frases intercaladas", AUTOMATICO),
    Inciso("XIV", "evitar o uso de substantivos no lugar de verbos", AUTOMATICO),
    Inciso("XV", "evitar redundâncias e palavras desnecessárias", AUTOMATICO),
    Inciso("XVI", "evitar palavras imprecisas", AUTOMATICO),
    Inciso(
        "XVII",
        "usar linguagem acessível à pessoa com deficiência, observados os "
        "requisitos de acessibilidade previstos na Lei nº 13.146, de 6 de "
        "julho de 2015 (Estatuto da Pessoa com Deficiência)",
        SINAL,
    ),
    Inciso("XVIII", "testar com o público-alvo se a mensagem está compreensível", FORA_DO_ALCANCE),
)

POR_NUMERO = {i.numero: i for i in INCISOS}
