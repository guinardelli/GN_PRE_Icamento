# PLAN_01 - Evolucao para App com Multiplas Calculadoras

## Resumo

Transformar o app atual em uma aplicacao desktop com home inicial e navegacao por calculadoras, mantendo a calculadora de Alca de icamento funcionando igual ao comportamento anterior.

Estrategia:

- Fazer em fases pequenas.
- Validar cada fase antes da proxima.
- Separar `MainWindow` da calculadora atual.
- Abrir cada calculadora em janela propria.
- Criar um registro simples para futuras calculadoras.

## Checklist Geral

- [x] Preservar comportamento atual da calculadora de alca.
- [x] Criar home inicial objetiva.
- [x] Permitir navegacao Home -> Janela da calculadora.
- [x] Voltar para home ao fechar a janela da calculadora.
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
- [x] Ajustar `MainWindow` para hospedar a home compacta.
- [x] Ajustar smoke test para acessar a calculadora no novo local.

Criterio de aceite:

- [x] Calculo automatico continua funcionando.
- [x] Memoria continua sendo gerada.
- [x] Exportacoes continuam disponiveis no menu da janela da calculadora.
- [ ] Exportacoes foram validadas manualmente.

## Fase 2 - Criar Home Inicial

Objetivo: adicionar tela inicial simples para acesso as calculadoras.

Checklist:

- [x] Criar `HomeWidget`.
- [x] Adicionar botao pequeno `Alca de icamento`.
- [x] Usar tema claro e visual simples.
- [x] Evitar textos longos ou aparencia de landing page.
- [x] Conectar clique do botao a abertura da calculadora.
- [x] Garantir que o app inicia na home.

Criterio de aceite:

- [x] App abre na home.
- [x] Botao `Alca de icamento` abre a janela da calculadora.
- [x] Calculadora mantem comportamento correto.

## Fase 3 - Criar Navegacao Principal

Objetivo: transformar `MainWindow` em home compacta e abrir calculadoras em janelas proprias.

Checklist:

- [x] Remover menus da home.
- [x] Remover botao `Inicio`.
- [x] Deixar a home com janela compacta.
- [x] Registrar tela da home.
- [x] Registrar janela da calculadora de alca.
- [x] Implementar navegacao Home -> Janela da calculadora.
- [x] Implementar retorno para Home ao fechar a janela da calculadora.
- [x] Manter acoes de exportacao/restauracao na janela da calculadora.
- [x] Evitar logica de calculo dentro da `MainWindow`.

Criterio de aceite:

- [x] Fluxo Home -> Alca -> fechar janela -> Home funciona via smoke test.
- [x] Reabrir a calculadora nao gera erro conhecido.
- [x] `MainWindow` fica responsavel apenas pela navegacao/container.

## Fase 4 - Registro Simples de Calculadoras

Objetivo: facilitar adicao futura de novas calculadoras.

Checklist:

- [x] Criar estrutura simples `CalculatorDefinition`.
- [x] Definir campos minimos: `id`, `title`, `description`, `widget_factory`.
- [x] Registrar calculadora `lifting`.
- [x] Fazer a home montar botoes/cards a partir do registro.
- [x] Fazer a navegacao abrir janela de calculadora pelo `id`.
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
- [x] Smoke test fecha a janela da calculadora e confirma retorno para home.
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
- [ ] Fechar janela da calculadora e confirmar retorno para home.
- [ ] Entrar novamente na calculadora.

## Assumptions

- A primeira versao multi-calculadoras tem apenas `Alca de icamento`.
- A regra de calculo nao foi alterada.
- Nao ha arquitetura de plugins agora.
- O foco e refatoracao segura e incremental.
- A home foi compactada e ficou sem menus.
- Cada nova calculadora deve ser um widget registrado em `app/ui/calculators/registry.py`.
