---
name: generate-test
description: Gera testes unitários completos para um módulo existente.
allowed-tools: Read, Write, Glob, Grep
---
Gere testes para o módulo: $ARGUMENTS (ex: "src/services/markdown_service.py").

1. Leia o módulo alvo em $ARGUMENTS.
2. Identifique todas as classes e métodos públicos (sem prefixo `_`).
3. Leia `tests/conftest.py` para fixtures disponíveis.
4. Para cada método público, crie pelo menos:
   - 1 teste de caso feliz (happy path).
   - 1 teste de caso de erro (exceção esperada).
   - 1 teste de edge case (lista vazia, None, string vazia, etc.).
5. Use nomenclatura: `test_{metodo}_{cenario}_{resultado_esperado}`.
6. Mocke dependências externas (banco, filesystem, SSH) — nunca a classe sob teste.
7. Salve em `tests/unit/test_{nome_do_modulo}.py`.
8. Rode `pytest tests/unit/test_{nome_do_modulo}.py -v` para verificar que os testes passam ou falham com erros esperados.