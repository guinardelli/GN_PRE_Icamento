# PLAN_03 - Migracao Paralela da Interface para Tkinter

## Resumo

Migrar a interface do app de PySide6 para Tkinter em fases controladas, mantendo a UI PySide6 funcionando ate a validacao final.

Objetivos principais:

- Reduzir o peso do executavel final removendo a dependencia de Qt/PySide6.
- Preservar a maior fidelidade visual e funcional possivel.
- Reaproveitar integralmente a camada `app/core/`.
- Evitar regressao mantendo a migracao paralela ate o corte final.

Estado final observado:

- A camada `app/core/` ja concentra os servicos e modelos de calculo.
- A UI oficial Tkinter esta em `app/tk_ui/`.
- O ponto de entrada oficial e `app/main.py`.
- `app/tk_main.py` permanece como wrapper de compatibilidade.
- A UI PySide6 em `app/ui/` foi removida no corte final.
- O `requirements.txt` nao possui dependencias de runtime.

## Regras da Migracao

- [ ] Nao remover nem alterar a UI PySide6 enquanto a UI Tkinter nao estiver validada.
- [ ] Nao duplicar regras de calculo na interface.
- [ ] Usar `app/core/` como fonte unica da logica de negocio.
- [ ] Criar a nova UI em `app/tk_ui/`.
- [ ] Criar um novo entrypoint `app/tk_main.py`.
- [ ] Manter `app/main.py` apontando para PySide6 ate a fase final.
- [ ] Portar os croquis com `tk.Canvas`.
- [ ] Manter o foco em fidelidade pratica, nao pixel-perfect absoluto.

## Fase 1 - Base Tkinter e Navegacao

Objetivo: criar a estrutura minima Tkinter e validar a navegacao sem portar calculos completos ainda.

- [x] Criar pacote `app/tk_ui/`.
- [x] Criar `app/tk_ui/__init__.py`.
- [x] Criar `app/tk_ui/styles.py` para estilos e constantes visuais.
- [x] Criar `app/tk_ui/main_window.py`.
- [x] Criar `app/tk_main.py`.
- [x] Implementar janela principal com titulo `GN Estruturas - Calculadoras`.
- [x] Recriar a home com `LabelFrame("NBR 9062")`.
- [x] Recriar a home com `LabelFrame("utilidades")`.
- [x] Adicionar botao `Alca de icamento`.
- [x] Adicionar botao `Comprimento de ancoragem`.
- [x] Adicionar botao `Conversor bitola/espacamento`.
- [x] Implementar janelas filhas vazias para as tres opcoes.
- [x] Ao abrir janela filha, ocultar a home.
- [x] Ao fechar janela filha, exibir a home.
- [x] Implementar `python app/tk_main.py --smoke-test`.
- [x] Smoke test deve validar abertura da home.
- [x] Smoke test deve validar abertura e fechamento das tres janelas.
- [x] Checkpoint: home Tkinter visualmente comparavel a home PySide6.

## Fase 2 - Conversor Bitola/Espacamento

Objetivo: portar o utilitario mais simples primeiro e validar o padrao de widgets Tkinter.

- [x] Criar `app/tk_ui/utilities/`.
- [x] Criar `app/tk_ui/utilities/__init__.py`.
- [x] Criar widget Tkinter do conversor em `app/tk_ui/utilities/rebar_converter.py`.
- [x] Reaproveitar `RebarConversionService`.
- [x] Reaproveitar `REBAR_CONVERSION_OPTIONS`.
- [x] Usar `LabelFrame("Armadura Original")`.
- [x] Usar `LabelFrame("Armadura Equivalente")`.
- [x] Usar `ttk.Combobox` para bitolas.
- [x] Usar campo numerico simples para espacamento original.
- [x] Usar campo somente leitura para espacamento equivalente.
- [x] Implementar botao `Converter`.
- [x] Exibir erro amigavel para espacamento invalido.
- [x] Validar caso `CA-50 - 8.0 mm`, `10 cm`, `CA-50 - 16.0 mm` resultando em `40.00`.
- [x] Remover ou manter apenas como referencia o preview isolado em `tools/preview_rebar_converter_tkinter.py`.
- [x] Checkpoint: conversor Tkinter aprovado visualmente e funcionalmente.

## Fase 3 - Calculadora Alca de Icamento

Objetivo: portar a calculadora de alca preservando layout, calculo automatico, resultados, memoria e croqui.

- [x] Criar `app/tk_ui/calculators/`.
- [x] Criar `app/tk_ui/calculators/__init__.py`.
- [x] Criar `app/tk_ui/calculators/lifting_calculator.py`.
- [x] Reaproveitar `LiftingVerifierService`.
- [x] Reaproveitar modelos e catalogos de `app/core/models.py`.
- [x] Recriar abas com `ttk.Notebook`.
- [x] Criar aba `Verificacao`.
- [x] Criar aba `Memoria de Calculo`.
- [x] Recriar grupos `Peca`, `Materiais`, `Icamento`, `Ancoragem`, `Coeficientes`.
- [x] Recriar grupo `Resultados`.
- [x] Implementar campos numericos com validacao.
- [x] Implementar combos equivalentes aos atuais.
- [x] Implementar recalculo automatico ao alterar entradas.
- [x] Implementar status OK/falha.
- [x] Implementar cores de resultado equivalentes.
- [x] Implementar memoria de calculo em `Text`.
- [x] Implementar botao `Copiar Memoria`.
- [x] Criar `app/tk_ui/sketches/lifting_sketch.py`.
- [x] Recriar croqui de alca com `tk.Canvas`.
- [x] Manter geometria, cores, labels e estado OK/falha proximos ao QPainter.
- [x] Adicionar smoke test para calculo inicial.
- [x] Adicionar smoke test para memoria preenchida.
- [x] Checkpoint: Alca Tkinter comparada lado a lado com PySide6.

## Fase 4 - Calculadora Comprimento de Ancoragem

Objetivo: portar a janela de ancoragem completa com suas tres familias de calculo.

- [x] Criar `app/tk_ui/calculators/anchorage_calculator.py`.
- [x] Reaproveitar `AnchorageVerifierService`.
- [x] Reaproveitar `LapSpliceService`.
- [x] Reaproveitar `PrestressingAnchorageService`.
- [x] Recriar janela com titulo `GN Pre - Ancoragem V 1.0`.
- [x] Recriar notebook principal.
- [x] Criar aba `Armadura passiva`.
- [x] Criar subaba `Verificacao`.
- [x] Criar subaba `Memoria de calculo`.
- [x] Criar aba `Emenda por transpasse`.
- [x] Criar aba `Cordoalhas/Fios`.
- [x] Portar campos e combos da armadura passiva.
- [x] Portar campos e combos da emenda por transpasse.
- [x] Portar campos e combos da protensao aderente.
- [x] Implementar recalculo automatico em todas as abas.
- [x] Manter regra visual de compressao: remover opcoes com gancho.
- [x] Manter aviso de ganchos nao considerados em compressao.
- [x] Implementar campos de resultado e status por aba.
- [x] Implementar memoria de calculo por aba.
- [x] Implementar botoes `Copiar Memoria`.
- [x] Criar `app/tk_ui/sketches/anchorage_sketch.py`.
- [x] Recriar croqui de ancoragem com `tk.Canvas`.
- [x] Manter geometria, cores, labels e estado OK/falha proximos ao QPainter.
- [x] Adicionar smoke test para abas principais.
- [x] Adicionar smoke test para memoria inicial.
- [x] Adicionar smoke test para regra de compressao.
- [x] Checkpoint: Ancoragem Tkinter comparada lado a lado com PySide6.

## Fase 5 - Estilo, Fidelidade e Usabilidade

Objetivo: fazer o acabamento visual depois das telas funcionarem.

- [x] Centralizar dimensoes de janela em `app/tk_ui/styles.py`.
- [x] Centralizar cores em `app/tk_ui/styles.py`.
- [x] Centralizar paddings, margins e gaps.
- [x] Padronizar `LabelFrame`.
- [x] Padronizar botoes.
- [x] Padronizar campos somente leitura.
- [x] Padronizar campos invalidos.
- [x] Padronizar status OK/falha.
- [x] Conferir textos e acentos.
- [x] Conferir ordem de foco.
- [x] Conferir navegacao por teclado basica.
- [x] Comparar capturas ou revisao visual lado a lado com PySide6.
- [x] Checkpoint: revisao visual completa aprovada.

## Fase 6 - Testes e Empacotamento Tkinter

Objetivo: preparar distribuicao leve com PyInstaller sem remover PySide6 ainda.

- [x] Manter testes de `core` existentes.
- [x] Criar testes de smoke Tkinter.
- [x] Adaptar testes de widget PySide6 para smoke Tkinter quando fizer sentido.
- [x] Manter testes PySide6 enquanto a UI antiga existir.
- [x] Criar `packaging/GN_PRE_Icamento_tk.spec`.
- [x] Criar `tools/build_tk_exe.ps1`.
- [x] Build Tkinter nao deve importar `PySide6`.
- [x] Build Tkinter deve rodar `--smoke-test` no executavel gerado.
- [x] Comparar tamanho do pacote Tkinter com o pacote PySide6 atual.
- [x] Registrar resultado da comparacao no README ou em nota de release.
- [x] Checkpoint: build Tkinter distribuivel validado.

## Fase 7 - Corte Final da PySide6

Objetivo: tornar Tkinter a interface oficial apenas depois de todos os checkpoints aprovados.

- [x] Confirmar que a UI Tkinter cobre todas as funcoes atuais.
- [x] Confirmar que o build Tkinter esta validado.
- [x] Trocar entrypoint oficial para Tkinter.
- [x] Atualizar comandos no README.
- [x] Remover `PySide6` do `requirements.txt`.
- [x] Remover ou arquivar `app/ui/`.
- [x] Remover specs PySide6 antigas ou marcar como legado.
- [x] Remover testes PySide6 ou converter para Tkinter.
- [x] Rodar `python -m pytest tests`.
- [x] Rodar `python app/tk_main.py --smoke-test`.
- [x] Rodar smoke test do executavel Tkinter.
- [x] Checkpoint final: app Tkinter substitui oficialmente a versao PySide6.

## Criterios de Aceite

- [x] App Tkinter abre no Windows.
- [x] Home Tkinter possui `NBR 9062` e `utilidades`.
- [x] Alca de icamento calcula automaticamente.
- [x] Comprimento de ancoragem calcula automaticamente.
- [x] Conversor bitola/espacamento calcula corretamente.
- [x] Memorias de calculo continuam disponiveis.
- [x] Botoes de copiar memoria funcionam.
- [x] Croquis existem em `Canvas` e representam os mesmos estados principais.
- [x] Testes de `core` continuam passando.
- [x] Smoke test Tkinter passa.
- [x] Executavel Tkinter e menor que o pacote PySide6 atual.
- [x] README contem comandos atualizados de execucao e build.

## Riscos e Cuidados

- Tkinter e ttk nao sao pixel-perfect em relacao ao Qt.
- Croquis com `Canvas` exigem cuidado porque substituem desenho QPainter manual.
- Testes de UI Tkinter devem focar comportamento, nao detalhes visuais frageis.
- A remocao de PySide6 so deve ocorrer na Fase 7.
- Mudancas de layout devem ser revisadas visualmente em Windows.

## Comandos Esperados

Durante a migracao:

```bash
python app/tk_main.py
python app/tk_main.py --smoke-test
python -m pytest tests
```

Depois da fase de empacotamento:

```powershell
powershell -ExecutionPolicy Bypass -File tools\build_exe.ps1
```
