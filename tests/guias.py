"""Trechos curtos de guias oficiais de linguagem simples, citados com a fonte.

Cada par traz o "antes" e o "depois" que o próprio guia dá. O texto foi
tirado do PDF com ``pdftotext`` em 09/10/2026 (quebra de linha desfeita,
hífen de fim de linha juntado, ligadura "ﬁ" escrita "fi") e conferido no PDF. O SHA-256 é o do PDF
baixado; a lista dos guias está no README.
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


_CAPES_SHA = "be94ff5edd1c2fc83b4dae942262ab386fa11f58c74159579cc28ad9d3f472b9"
_ANVISA_SHA = "104e55792cedd2d813acbc7aec7176e1e3ef285f1a5d8cb0c4a5dc05bb20fb60"
_TJGO_SHA = "8a53da863265c86396c419c9004217c34716d5c74700d5f6aa0f8647d885ad32"
_TREAL_SHA = "b503e8c5dd7d32b08624811b7f7635afb7beb40ed0c31a0c7a0cd82b018d3cdf"
_CAPES_10 = Fonte("CAPES, O uso da Linguagem Simples na CAPES (2026)", 10, CAPES, _CAPES_SHA)
_ANVISA_13 = Fonte("Anvisa, Guia de Linguagem Simples, 1ª ed.", 13, ANVISA, _ANVISA_SHA)
_ANVISA_14 = Fonte("Anvisa, Guia de Linguagem Simples, 1ª ed.", 14, ANVISA, _ANVISA_SHA)
_TJGO_12 = Fonte("TJGO, Guia de Linguagem Simples do TJGO", 12, TJGO, _TJGO_SHA)  # rótulo em ícone, conferido na página
_TREAL_15 = Fonte("TRE-AL, Linguagem Simples – Cartilha (2024)", 15, TREAL, _TREAL_SHA)  # conferido na página

# Inciso XII.
PASSIVA = (
    Par(_ANVISA_14, "A documentação completa foi entregue pela empresa.",
        "A empresa entregou a documentação completa."),
    Par(_ANVISA_14, "O Sistema Nacional de Vigilância Sanitária (SNVS) é coordenado pela Anvisa.",
        "A Anvisa coordena o Sistema Nacional de Vigilância Sanitária (SNVS)."),
    Par(_ANVISA_14, "Dez lotes do medicamento serão interditados pela Anvisa.",
        "A Anvisa interditará dez lotes do medicamento."),
)
# A CAPES põe este par em "Prefira a voz ativa", mas o "antes" não tem verbo
# na voz passiva: "é responsabilidade" é verbo de ligação com substantivo.
PASSIVA_CAPES = Par(_CAPES_10, "A gestão do programa é responsabilidade da CAPES.",
                    "A CAPES é responsável pela gestão do programa.")

# Inciso XIII.
INTERCALADA_CAPES = Par(
    _CAPES_10, "O documento, que deve ser apresentado pelo requerente, é obrigatório.",
    "O requerente deve apresentar o documento obrigatório.",
)

# Inciso XIV.
NOMINALIZACAO = (
    Par(_CAPES_10, "Obtenção de bolsa de pós-graduação no país.", "Obter bolsa de pós-graduação no país."),
    Par(_ANVISA_13, "O Sistema Parlatório permite o agendamento de audiências presenciais ou virtuais.",
        "O Sistema Parlatório permite agendar audiências presenciais ou virtuais."),
    Par(_ANVISA_13, "A Anvisa determinou que o fabricante promova o recolhimento do estoque do produto.",
        "A Anvisa determinou que o fabricante recolha o estoque do produto."),
    Par(_ANVISA_13, "As áreas responsáveis farão a análise do pedido de ampliação da indicação da vacina.",
        "As áreas responsáveis analisarão o pedido para ampliar a indicação da vacina."),
    Par(_TJGO_12, "Faça a identificação do réu.", "Identifique o réu."),
    Par(_TREAL_15, "Para a prevenção da Covid-19, recomenda-se a higienização das mãos.",
        "Para prevenir a Covid-19, higienize as mãos."),
    Par(_TREAL_15, "Fazer o encaminhamento do eleitor ao cartório eleitoral.",
        "Encaminhar o eleitor ao cartório eleitoral."),
)

# Inciso XV. A CAPES, item 14, "Evite redundâncias e palavras desnecessárias".
_CAPES_11 = Fonte("CAPES, O uso da Linguagem Simples na CAPES (2026)", 11, CAPES, _CAPES_SHA)
REDUNDANCIA_CAPES = Par(_CAPES_11, "Compareça pessoalmente ao local.", "Compareça ao local.")

# Inciso XVII. O eMAG 3.1 é uma página, não um PDF: "pagina" 0. O HTML foi
# baixado em 10/10/2026 (o SHA-256 é o dele); os exemplos são o código que a
# própria página traz, copiado como está (na tabela, sem o recuo das linhas).
EMAG = "https://emag.governoeletronico.gov.br/"
_EMAG = Fonte("eMAG 3.1, Modelo de Acessibilidade em Governo Eletrônico (abril de 2014)", 0, EMAG,
              "200884cddfa8a769473899f2db6cd34cc819a6573439f9409eec7806ea368d0f")
# Recomendação 3.5, "Exemplo Incorreto" e "Exemplo Correto".
LINK_EMAG = Par(
    _EMAG,
    '<p><a id="r19_c" href="#r19_c">Clique aqui</a> para saber mais a respeito de acessibilidade.</p>',
    '<p><a id="r19_i" href="#r19_i">Saiba mais a respeito de acessibilidade</a></p>',
)
# Recomendação 3.5 (o texto do link, certo nos dois exemplos), 3.6 (exemplos
# 1 e 2) e 3.10 (exemplo 1, com caption, thead, tfoot e tbody).
BONS_EMAG = (
    '<p> <a href="notici5125.html">Leia mais notícias sobre Educação Superior</a> </p>',
    '<img src="foto-porto-alegre.jpg" alt="Foto de uma bicicleta de carga verde com caixas '
    'laranjas encostada numa parede"  />',
    '<a href="http://www.dominiopublico.gov.br/">      <img src="guia.png" alt="Guia de Serviços – '
    'Consulte serviços públicos de forma fácil" />      </a>',
    "<table><caption>Demonstrativo do Patrimônio</caption><thead><tr><th>Tipos</th>"
    "<th>Valores (R$)</th><th>Percentual</th></tr></thead><tfoot><tr><td>Total</td>"
    "<td>110.740,22</td><td>100%</td></tr></tfoot><tbody><tr><td>Recursos Financeiro</td>"
    "<td>56.879,63</td><td>51,36%</td></tr><tr><td>Bens Móveis</td><td>25.691,23</td>"
    "<td>23,20%</td></tr><tr><td>Bens Imóveis</td><td>28.169,36</td><td>25,44%</td></tr>"
    "</tbody></table>",
)
