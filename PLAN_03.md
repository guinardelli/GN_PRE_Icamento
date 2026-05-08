# PLAN_03 - Migracao Paralela da Interface para Tkinter

## Resumo

Migrar a interface do app de PySide6 para Tkinter em fases controladas, mantendo a UI PySide6 funcionando ate a validacao final.

Objetivos principais:

- Reduzir o peso do executavel final removendo a dependencia de Qt/PySide6.
- Preservar a maior fidelidade visual e funcional possivel.
- Reaproveitar integralmente a camada `app/core/`.
- Evitar regressao mantendo a migracao paralela ate o corte final.

Estado atual observado:

- A camada `app/core/` ja concentra os servicos e modelos de calculo.
- A UI atual PySide6 esta em `app/ui/`.
- Ja existe um preview Tkinter isolado do conversor em `tools/preview_rebar_converter_tkinter.py`.
- Ainda nao existe `app/tk_ui/`.
- O `requirements.txt` ainda contem `PySide6` e so deve ser alterado no corte final.

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
- [ ] Checkpoint: Alca Tkinter comparada lado a lado com PySide6.

## Fase 4 - Calculadora Comprimento de Ancoragem

Objetivo: portar a janela de ancoragem completa com suas tres familias de calculo.

- [ ] Criar `app/tk_ui/calculators/anchorage_calculator.py`.
- [ ] Reaproveitar `AnchorageVerifierService`.
- [ ] Reaproveitar `LapSpliceService`.
- [ ] Reaproveitar `PrestressingAnchorageService`.
- [ ] Recriar janela com titulo `GN Pre - Ancoragem V 1.0`.
- [ ] Recriar notebook principal.
- [ ] Criar aba `Armadura passiva`.
- [ ] Criar subaba `Verificacao`.
- [ ] Criar subaba `Memoria de calculo`.
- [ ] Criar aba `Emenda por transpasse`.
- [ ] Criar aba `Cordoalhas/Fios`.
- [ ] Portar campos e combos da armadura passiva.
- [ ] Portar campos e combos da emenda por transpasse.
- [ ] Portar campos e combos da protensao aderente.
- [ ] Implementar recalculo automatico em todas as abas.
- [ ] Manter regra visual de compressao: remover opcoes com gancho.
- [ ] Manter aviso de ganchos nao considerados em compressao.
- [ ] Implementar campos de resultado e status por aba.
- [ ] Implementar memoria de calculo por aba.
- [ ] Implementar botoes `Copiar Memoria`.
- [ ] Criar `app/tk_ui/sketches/anchorage_sketch.py`.
- [ ] Recriar croqui de ancoragem com `tk.Canvas`.
- [ ] Manter geometria, cores, labels e estado OK/falha proximos ao QPainter.
- [ ] Adicionar smoke test para abas principais.
- [ ] Adicionar smoke test para memoria inicial.
- [ ] Adicionar smoke test para regra de compressao.
- [ ] Checkpoint: Ancoragem Tkinter comparada lado a lado com PySide6.

## Fase 5 - Estilo, Fidelidade e Usabilidade

Objetivo: fazer o acabamento visual depois das telas funcionarem.

- [ ] Centralizar dimensoes de janela em `app/tk_ui/styles.py`.
- [ ] Centralizar cores em `app/tk_ui/styles.py`.
- [ ] Centralizar paddings, margins e gaps.
- [ ] Padronizar `LabelFrame`.
- [ ] Padronizar botoes.
- [ ] Padronizar campos somente leitura.
- [ ] Padronizar campos invalidos.
- [ ] Padronizar status OK/falha.
- [ ] Conferir textos e acentos.
- [ ] Conferir ordem de foco.
- [ ] Conferir navegacao por teclado basica.
- [ ] Comparar capturas ou revisao visual lado a lado com PySide6.
- [ ] Checkpoint: revisao visual completa aprovada.

## Fase 6 - Testes e Empacotamento Tkinter

Objetivo: preparar distribuicao leve com PyInstaller sem remover PySide6 ainda.

- [ ] Manter testes de `core` existentes.
- [ ] Criar testes de smoke Tkinter.
- [ ] Adaptar testes de widget PySide6 para smoke Tkinter quando fizer sentido.
- [ ] Manter testes PySide6 enquanto a UI antiga existir.
- [ ] Criar `packaging/GN_PRE_Icamento_tk.spec`.
- [ ] Criar `tools/build_tk_exe.ps1`.
- [ ] Build Tkinter nao deve importar `PySide6`.
- [ ] Build Tkinter deve rodar `--smoke-test` no executavel gerado.
- [ ] Comparar tamanho do pacote Tkinter com o pacote PySide6 atual.
- [ ] Registrar resultado da comparacao no README ou em nota de release.
- [ ] Checkpoint: build Tkinter distribuivel validado.

## Fase 7 - Corte Final da PySide6

Objetivo: tornar Tkinter a interface oficial apenas depois de todos os checkpoints aprovados.

- [ ] Confirmar que a UI Tkinter cobre todas as funcoes atuais.
- [ ] Confirmar que o build Tkinter esta validado.
- [ ] Trocar entrypoint oficial para Tkinter.
- [ ] Atualizar comandos no README.
- [ ] Remover `PySide6` do `requirements.txt`.
- [ ] Remover ou arquivar `app/ui/`.
- [ ] Remover specs PySide6 antigas ou marcar como legado.
- [ ] Remover testes PySide6 ou converter para Tkinter.
- [ ] Rodar `python -m pytest tests`.
- [ ] Rodar `python app/tk_main.py --smoke-test`.
- [ ] Rodar smoke test do executavel Tkinter.
- [ ] Checkpoint final: app Tkinter substitui oficialmente a versao PySide6.

## Criterios de Aceite

- [ ] App Tkinter abre no Windows.
- [ ] Home Tkinter possui `NBR 9062` e `utilidades`.
- [ ] Alca de icamento calcula automaticamente.
- [ ] Comprimento de ancoragem calcula automaticamente.
- [ ] Conversor bitola/espacamento calcula corretamente.
- [ ] Memorias de calculo continuam disponiveis.
- [ ] Botoes de copiar memoria funcionam.
- [ ] Croquis existem em `Canvas` e representam os mesmos estados principais.
- [ ] Testes de `core` continuam passando.
- [ ] Smoke test Tkinter passa.
- [ ] Executavel Tkinter e menor que o pacote PySide6 atual.
- [ ] README contem comandos atualizados de execucao e build.

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
powershell -ExecutionPolicy Bypass -File tools\build_tk_exe.ps1
```
