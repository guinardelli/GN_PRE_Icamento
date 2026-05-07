# PLAN_02 - Calculadora de Comprimento de Ancoragem NBR 6118

## Resumo

Criar uma nova calculadora para comprimento de ancoragem de barras passivas conforme NBR 6118.

Escopo da primeira versão:

- Barras passivas.
- Casos de tração e compressão.
- Cálculo com `As,calc` e `As,ef`.
- Comparação entre comprimento necessário e comprimento disponível.
- Memória de cálculo em texto.
- Sem transpasses, feixes, telas soldadas ou armaduras ativas nesta fase.

## Checklist Geral

- [x] Definir modelo de cálculo normativo.
- [x] Criar serviço de cálculo independente da interface.
- [x] Criar widget PySide6 da calculadora.
- [x] Registrar nova calculadora na home.
- [x] Implementar memória de cálculo.
- [x] Criar testes automatizados da lógica principal.
- [x] Atualizar README.
- [x] Validar execução local.

## Fase 0 - Conferência Normativa

Objetivo: travar as premissas antes de implementar.

Checklist:

- [x] Confirmar versão adotada da NBR 6118.
- [x] Conferir fórmulas de `fctm`, `fctd`, `fbd`, `lb`, `lb,min` e `lb,nec`.
- [x] Confirmar coeficientes para boa e má aderência.
- [x] Confirmar regras para tração.
- [x] Confirmar regras para compressão.
- [x] Confirmar restrições para uso de gancho.
- [x] Registrar premissas no README e na memória de cálculo.

Critério de aceite:

- [x] Premissas normativas estão claras antes da implementação.

## Fase 1 - Modelo e Serviço em Core

Objetivo: implementar a lógica testável fora da interface.

Checklist:

- [x] Criar modelos de entrada e resultado da calculadora.
- [x] Criar enums para tipo de aço, condição de aderência, solicitação e tipo de ancoragem.
- [x] Implementar cálculo de resistências do concreto.
- [x] Implementar cálculo de tensão de aderência.
- [x] Implementar cálculo de comprimento básico de ancoragem.
- [x] Implementar cálculo de comprimento mínimo.
- [x] Implementar cálculo de comprimento necessário.
- [x] Implementar verificação contra comprimento disponível.
- [x] Implementar validações de entrada.
- [x] Gerar mensagens claras para combinações inválidas.

Critério de aceite:

- [x] Serviço calcula sem depender de PySide6.
- [x] Entradas inválidas geram erro controlado.
- [x] Resultado informa valores intermediários e status final.

## Fase 2 - Widget PySide6

Objetivo: criar a interface da nova calculadora.

Checklist:

- [x] Criar `AnchorageCalculatorWidget`.
- [x] Organizar entradas em grupos simples.
- [x] Usar tema claro e widgets nativos.
- [x] Recalcular automaticamente ao alterar entradas.
- [x] Exibir status `ATENDE`, `NÃO ATENDE` ou `ENTRADA INVÁLIDA`.
- [x] Exibir resultados principais em campos somente leitura.
- [x] Exibir memória de cálculo em aba própria.
- [x] Implementar ação para copiar memória.
- [x] Implementar ação para restaurar padrões.

Critério de aceite:

- [x] Usuário consegue calcular e verificar ancoragem sem fluxo manual complexo.
- [x] Interface não contém regra de negócio pesada.

## Fase 3 - Integração com App

Objetivo: adicionar a calculadora ao fluxo atual de múltiplas calculadoras.

Checklist:

- [x] Registrar a calculadora em `app/ui/calculators/registry.py`.
- [x] Adicionar título `Comprimento de ancoragem`.
- [x] Adicionar descrição objetiva para tooltip na home.
- [x] Garantir abertura em janela própria.
- [x] Garantir retorno para home ao fechar janela.
- [x] Ajustar menus para ações disponíveis no widget.

Critério de aceite:

- [x] Fluxo Home -> Calculadora de ancoragem -> fechar -> Home funciona.

## Fase 4 - Testes

Objetivo: validar a lógica principal com casos automatizados.

Checklist:

- [x] Criar testes para caso base em tração.
- [x] Criar testes para caso base em compressão.
- [x] Testar boa aderência.
- [x] Testar má aderência.
- [x] Testar redução por `As,calc / As,ef`.
- [x] Testar limite de comprimento mínimo.
- [x] Testar bloqueio de gancho em compressão.
- [x] Testar entradas inválidas.
- [x] Rodar compilação Python dos arquivos alterados.

Critério de aceite:

- [x] Testes principais passam localmente.

## Fase 5 - Documentação e Validação Manual

Objetivo: deixar uso e premissas documentados.

Checklist:

- [x] Atualizar lista de calculadoras no README.
- [x] Documentar entradas.
- [x] Documentar saídas.
- [x] Documentar fórmulas adotadas.
- [x] Documentar limitações da v1.
- [x] Abrir aplicação manualmente.
- [x] Abrir calculadora de ancoragem.
- [x] Alterar entradas e confirmar recalculo.
- [x] Conferir memória de cálculo.
- [x] Conferir mensagens de entrada inválida.

Critério de aceite:

- [x] README descreve corretamente a nova calculadora.
- [x] Aplicação abre e a calculadora funciona no Windows.

## Assumptions

- A calculadora usa NBR 6118 como referência normativa principal.
- A primeira versão não inclui transpasses.
- A primeira versão não inclui feixes de barras.
- A primeira versão não inclui telas soldadas.
- A primeira versão não inclui armaduras ativas.
- A validação final dos resultados continua sendo responsabilidade do engenheiro responsável.
