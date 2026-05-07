# PLAN_01 - Evolucao para App com Multiplas Calculadoras

## Resumo

Transformar o app atual em uma aplicacao desktop com home inicial e navegacao por calculadoras, mantendo a calculadora de Alca de icamento funcionando igual ao comportamento anterior.

Estrategia:

- Fazer em fases pequenas.
- Validar cada fase antes da proxima.
- Separar `MainWindow` da calculadora atual.
- Usar `QStackedWidget` para navegacao.
- Criar um registro simples para futuras calculadoras.

## Checklist Geral

- [x] Preservar comportamento atual da calculadora de alca.
- [x] Criar home inicial objetiva.
- [x] Permitir navegacao Home -> Calculadora.
- [x] Permitir voltar da calculadora para Home.
- [x] Deixar estrutura pronta para novas calculadoras.
- [x] Atualizar smoke test.
- [x] Atualizar README.
- [x] Validar execucao automatizada local no Windows.
- [ ] Validar manualmente a interface no Windows.

## Fase 0 - Baseline e Validacao Atual

Objetivo: confirmar o estado atual antes de refatorar.

Checklist:

- [x] Rodar `python app/main.py --smoke-test`.
- [ ] Abrir aplicacao manualmente.
- [x] Confirmar calculo automatico inicial via smoke test.
- [x] Confirmar geracao da memoria de calculo via smoke test.
- [ ] Confirmar exportacao de memoria `.txt` manualmente.
- [ ] Confirmar exportacao de desenho `.svg` manualmente.
- [x] Registrar problemas existentes antes da refatoracao, se houver.

Criterio de aceite:

- [x] App atual funciona antes de qualquer alteracao estrutural.

## Fase 1 - Extrair Calculadora de Alca para Widget Proprio

Objetivo: separar a calculadora atual da janela principal.

Checklist:

- [x] Criar widget dedicado `LiftingCalculatorWidget`.
- [x] Mover interface atual da calculadora para esse widget.
- [x] Manter `LiftingVerifierService` em `core`.
- [x] Manter modelos em `core.models`.
- [x] Manter exportacao SVG em `infrastructure`.
- [x] Ajustar `MainWindow` para hospedar calculadoras.
- [x] Ajustar smoke test para acessar a calculadora no novo local.

Criterio de aceite:

- [x] Calculo automatico continua funcionando.
- [x] Memoria continua sendo gerada.
- [x] Exportacoes continuam disponiveis no menu.
- [ ] Exportacoes foram validadas manualmente.

## Fase 2 - Criar Home Inicial

Objetivo: adicionar tela inicial simples para acesso as calculadoras.

Checklist:

- [x] Criar `HomeWidget`.
- [x] Adicionar botao/card `Alca de icamento`.
- [x] Usar tema claro e visual simples.
- [x] Evitar textos longos ou aparencia de landing page.
- [x] Conectar clique do botao a abertura da calculadora.
- [x] Garantir que o app inicia na home.

Criterio de aceite:

- [x] App abre na home.
- [x] Botao `Alca de icamento` abre a calculadora.
- [x] Calculadora mantem comportamento correto.

## Fase 3 - Criar Navegacao Principal

Objetivo: transformar `MainWindow` em container de navegacao.

Checklist:

- [x] Adicionar `QStackedWidget` na `MainWindow`.
- [x] Registrar tela da home.
- [x] Registrar tela da calculadora de alca.
- [x] Implementar navegacao Home -> Calculadora.
- [x] Implementar voltar Calculadora -> Home.
- [x] Manter acoes globais na janela principal.
- [x] Evitar logica de calculo dentro da `MainWindow`.

Criterio de aceite:

- [x] Fluxo Home -> Alca -> Home funciona via smoke test.
- [x] Reabrir a calculadora nao gera erro conhecido.
- [x] `MainWindow` fica responsavel apenas pela navegacao/container.

## Fase 4 - Registro Simples de Calculadoras

Objetivo: facilitar adicao futura de novas calculadoras.

Checklist:

- [x] Criar estrutura simples `CalculatorDefinition`.
- [x] Definir campos minimos: `id`, `title`, `description`, `widget_factory`.
- [x] Registrar calculadora `lifting`.
- [x] Fazer a home montar botoes/cards a partir do registro.
- [x] Fazer a navegacao abrir calculadora pelo `id`.
- [x] Evitar arquitetura de plugins neste momento.

Criterio de aceite:

- [x] Nova calculadora futura exige criar widget e adicionar definicao ao registro.
- [x] Nao ha dependencia circular entre `ui`, `core` e `infrastructure`.

## Fase 5 - Documentacao, Nome e Empacotamento

Objetivo: alinhar documentacao e metadados ao novo app multi-calculadoras.

Checklist:

- [x] Alterar `APP_NAME` para `GN PRE - Calculadoras`.
- [x] Atualizar `README.md` com a nova estrutura do app.
- [x] Documentar que a primeira calculadora e `Alca de icamento`.
- [x] Documentar como adicionar futuras calculadoras.
- [x] Conferir scripts de empacotamento.
- [x] Manter renome do executavel para uma fase futura.

Criterio de aceite:

- [x] README descreve corretamente o app multi-calculadoras.
- [x] Execucao local continua sendo `python app/main.py`.
- [x] Empacotamento nao foi alterado nesta fase.

## Testes e Validacoes

Checklist tecnico:

- [x] Smoke test abre aplicacao em modo offscreen.
- [x] Smoke test navega da home para `Alca de icamento`.
- [x] Smoke test confirma resultado inicial.
- [x] Smoke test confirma memoria com `MEMORIA DE CALCULO`.
- [ ] Testes unitarios de logica serao adicionados quando houver suite ativa no projeto.

Checklist manual:

- [ ] Abrir aplicacao.
- [ ] Entrar na calculadora de alca.
- [ ] Alterar entradas.
- [ ] Confirmar recalculo automatico.
- [ ] Copiar memoria.
- [ ] Exportar memoria `.txt`.
- [ ] Exportar desenho `.svg`.
- [ ] Voltar para home.
- [ ] Entrar novamente na calculadora.

## Assumptions

- A primeira versao multi-calculadoras tem apenas `Alca de icamento`.
- A regra de calculo nao foi alterada.
- Nao ha arquitetura de plugins agora.
- O foco e refatoracao segura e incremental.
- Mudancas visuais foram minimas.
- Cada nova calculadora deve ser um widget registrado em `app/ui/calculators/registry.py`.

