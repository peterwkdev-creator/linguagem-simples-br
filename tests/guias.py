"""Trechos curtos de guias oficiais de linguagem simples, citados com a fonte.

Cada par traz o "antes" e o "depois" que o próprio guia dá. O texto foi
tirado do PDF com ``pdftotext`` em 09/10/2026 (quebra de linha desfeita,
hífen de fim de linha juntado, ligadura "ﬁ" escrita "fi") e conferido no PDF. O SHA-256 é o do PDF
baixado; o índice completo está em ``corpus/fontes.md`` do projeto.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Fonte:
    guia: str
    pagina: int  # página do arquivo PDF
    url: str
    sha256: str


TJGO = "https://docs.tjgo.jus.br/institucional/gestaoestrategica/guia_simples_facil.pdf"
CAPES = (
    "https://www.gov.br/capes/pt-br/centrais-de-conteudo/documentos/"
    "cartilha-uso-da-linguagem-simples-na-capes.pdf/@@display-file/file"
)
ANVISA = (
    "https://www.gov.br/anvisa/pt-br/centraisdeconteudo/publicacoes/gestao/"
    "comunicacao/guia-de-linguagem-simples-anvisa.pdf/@@download/file"
)
TREAL = (
    "https://static.tre-al.jus.br/portal/o-tre/comissoes/acessibilidade-e-inclusao/"
    "tre-al-cartilha-linguagem-simples-2024.pdf"
)


@dataclass(frozen=True)
class Par:
    fonte: Fonte
    antes: str
    depois: str
    limiar_do_guia: int = None  # para o inciso II, o número que o guia dá


# Inciso II, com os rótulos em ícone (✗ e ✓), conferidos na página renderizada.
FRASE_TJGO = Par(
    Fonte("TJGO, Guia de Linguagem Simples do TJGO", 9, TJGO,
          "8a53da863265c86396c419c9004217c34716d5c74700d5f6aa0f8647d885ad32"),
    "Certifico e dou fé que, dando cumprimento ao mandado subscrito extraído "
    "dos autos em epígrafe, dirigi-me ao endereço informado, e após "
    "diligências em dias e horários distintos e em observância às "
    "formalidades legais verifiquei a veracidade do endereço ora informado no "
    "vertente mandado.",
    "Certifico e dou fé que fui ao endereço informado nos autos em dias e "
    "horários diferentes. Assim, verifiquei que o endereço era verdadeiro.",
    limiar_do_guia=20,
)

FRASE_CAPES = Par(
    Fonte("CAPES, O uso da Linguagem Simples na CAPES (2026)", 8, CAPES,
          "be94ff5edd1c2fc83b4dae942262ab386fa11f58c74159579cc28ad9d3f472b9"),
    "A Ouvidoria, setor que intermedia os interesses dos cidadãos e da "
    "administração pública, atua como facilitadora na promoção da "
    "transparência pública, favorecendo o controle social e do exercício da "
    "democracia por parte dos cidadãos.",
    "A Ouvidoria é o setor que intermedia os interesses dos cidadãos e da "
    "administração pública. Ela atua como facilitadora na promoção da "
    "transparência pública, em favor do controle social e o exercício da "
    "democracia pelos cidadãos.",
    limiar_do_guia=25,
)

FRASE_ANVISA = Par(
    Fonte("Anvisa, Guia de Linguagem Simples, 1ª ed.", 13, ANVISA,
          "104e55792cedd2d813acbc7aec7176e1e3ef285f1a5d8cb0c4a5dc05bb20fb60"),
    "O patrocinador do estudo (pessoa física ou jurídica, pública ou privada) "
    "tem obrigação de notificar à Anvisa os eventos adversos graves, por meio "
    "de formulário específico no portal da Agência (www.anvisa.gov.br), no "
    "prazo máximo de 15 (quinze) dias corridos, a partir do conhecimento do "
    "fato, excetuando-se os casos envolvendo óbito do paciente, situação em "
    "que a notificação deve ocorrer em até 7 (sete) dias corridos.",
    "O patrocinador do estudo (pessoa física ou jurídica, pública ou privada) "
    "tem obrigação de notificar à Anvisa os eventos adversos graves. A "
    "notificação é feita por meio de formulário específico no portal da "
    "Agência (www.anvisa.gov.br). O prazo máximo é de 15 (quinze) dias "
    "corridos, a partir do conhecimento do fato. Há uma exceção: casos "
    "envolvendo óbito do paciente devem ser notificados em até 7 (sete) dias "
    "corridos.",
    limiar_do_guia=25,  # o guia diz "entre 20 e 25"
)

# Inciso VIII.
SIGLA_CAPES = Par(
    Fonte("CAPES, O uso da Linguagem Simples na CAPES (2026)", 9, CAPES,
          "be94ff5edd1c2fc83b4dae942262ab386fa11f58c74159579cc28ad9d3f472b9"),
    "O atendimento será feito pela DTI.",
    "O atendimento será feito pela Diretoria de Tecnologia da Informação (DTI).",
)

SIGLA_ANVISA_LACEN = Par(
    Fonte("Anvisa, Guia de Linguagem Simples, 1ª ed.", 12, ANVISA,
          "104e55792cedd2d813acbc7aec7176e1e3ef285f1a5d8cb0c4a5dc05bb20fb60"),
    "O Lacen identificou alterações na qualidade do produto.",
    "O Laboratório Central de Saúde Pública (Lacen) identificou alterações na "
    "qualidade do produto.",
)

# Texto que o guia dá como bom ("Depois"), com quatro parágrafos e três siglas.
ANVISA_SEI_DEPOIS = (
    "Usuários (pessoas físicas) que precisem assinar documentos da Anvisa, "
    "como contratos, convênios e acordos, devem se cadastrar no Sistema "
    "Eletrônico de Informações (SEI).\n\n"
    "Para saber como se cadastrar, consulte o passo a passo no Manual de "
    "Usuário Externo, disponível em www.anvisa.gov.br.\n\n"
    "O cadastro é pessoal e intransferível. Isso significa que o usuário é "
    "responsável pelas ações que fizer no sistema e pode ser punido por atos "
    "irregulares.\n\n"
    "O SEI é uma plataforma de gestão de documentos e processos eletrônicos. "
    "O sistema faz parte do Processo Eletrônico Nacional (PEN), uma "
    "iniciativa de órgãos de diversas esferas da administração pública."
)
ANVISA_SEI_FONTE = Fonte(
    "Anvisa, Guia de Linguagem Simples, 1ª ed.", 11, ANVISA,
    "104e55792cedd2d813acbc7aec7176e1e3ef285f1a5d8cb0c4a5dc05bb20fb60",
)

# Inciso III: os dois parágrafos em que o guia ensina parágrafo curto e frase
# afirmativa (o próprio texto do guia, que segue a regra que dá).
TREAL_PARAGRAFOS = (
    "Assim como as frases, os parágrafos devem ser curtos e objetivos. "
    "Parágrafos muito longos desencorajam o leitor a iniciar a leitura. A "
    "recomendação é que um parágrafo não tenha mais que 150 palavras e, no "
    "máximo, oito frases. Além disso, não esqueça: mantenha apenas um tópico "
    "por parágrafo.\n\n"
    "Sempre que possível, use formas afirmativas, porque toda negação requer "
    "trabalho mental. E é muito comum que o leitor não perceba o “NÃO” na "
    "frase. Em algumas situações, frases negativas podem ser utilizadas. O "
    "importante, nestes casos, é evitar a combinação de vários elementos "
    "negativos."
)
TREAL_FONTE = Fonte(
    "TRE-AL, Linguagem Simples – Cartilha (2024)", 14, TREAL,
    "b503e8c5dd7d32b08624811b7f7635afb7beb40ed0c31a0c7a0cd82b018d3cdf",
)
