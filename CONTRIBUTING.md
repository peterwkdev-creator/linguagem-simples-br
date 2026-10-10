# Como contribuir

Resultado diferente do esperado ou caso que falta: abra uma issue pelo
modelo "Resultado diferente do esperado". Para mandar código:

- Os testes rodam do checkout, sem instalar nada:

  ```bash
  python -m unittest
  ```

- Só a biblioteca padrão: nenhuma dependência.
- Todo limiar e toda entrada de léxico têm fonte: o guia oficial, a página e a data de consulta. Detector novo vem com as duas provas: pega o defeito plantado e não dispara no texto que o guia dá como bom.
- Todo caso novo tem teste, com o resultado esperado escrito à mão no
  próprio teste.
- Exemplos e testes só com dados inventados: nada de dado real de pessoa ou
  de empresa.
- Código, mensagens e documentação em português do Brasil.
- Mudança de comportamento entra no [CHANGELOG.md](CHANGELOG.md).
- Código próprio: não traga código copiado de outro projeto, mesmo de
  licença livre. O que você contribui sai sob a [licença MIT](LICENSE) do
  projeto.
