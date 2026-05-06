# Plano Final de Melhorias - GN_PRE_Icamento

Este plano consolida as correcoes e melhorias identificadas na auditoria tecnica para estabilizar a versao 1.0 do aplicativo desktop de verificacao de icamento.

## Objetivo

Garantir que a aplicacao esteja estavel, previsivel e pronta para uso em producao, com foco em:

- Validacao robusta das regras de negocio.
- Integridade dos dados de entrada e saida.
- Interface resiliente a uso real.
- Infraestrutura coerente com o escopo da versao.
- Testes cobrindo casos criticos de engenharia.
- Documentacao alinhada ao comportamento real do codigo.

## 1. Correcoes Criticas

### 1.1 Validar coeficientes no core

Status: OK - implementado na primeira parte.

Arquivo principal: `app/core/services.py`

Problema:

- `beta_a` e `gamma_n` nao sao validados pelo servico.
- Chamadas diretas ao core podem passar valores negativos ou zero.
- Isso pode gerar carga majorada negativa, fator de seguranca infinito e aprovacao indevida.

Acao:

- Adicionar validacao em `_validate`.
- Exigir `beta_a > 0`.
- Exigir `gamma_n > 0`.
- Retornar `ValidationError` com mensagens claras.

Testes obrigatorios:

- [x] `beta_a = 0` deve falhar.
- [x] `beta_a < 0` deve falhar.
- [x] `gamma_n = 0` deve falhar.
- [x] `gamma_n < 0` deve falhar.

### 1.2 Rejeitar valores nao finitos

Status: OK - implementado na primeira parte.

Arquivo principal: `app/core/services.py`

Problema:

- Entradas `NaN`, `inf` e `-inf` passam pelas comparacoes atuais.
- Isso pode gerar resultados `nan` e estados incoerentes como `capacity_is_ok=True`.

Acao:

- Criar uma funcao auxiliar privada para validar numeros finitos, por exemplo `_ensure_finite_positive`.
- Aplicar a todos os campos numericos:
  - `fckj_mpa`
  - `fck_28_mpa`
  - `volume_m3`
  - `concrete_unit_weight_tf_m3`
  - `inclination_deg`
  - `available_anchorage_cm`
  - `beta_a`
  - `gamma_n`

Testes obrigatorios:

- [x] Cada campo numerico relevante com `float("nan")` deve falhar.
- [x] Cada campo numerico relevante com `float("inf")` deve falhar.
- [x] Cada campo numerico relevante com `float("-inf")` deve falhar.

### 1.3 Validar enums explicitamente

Status: OK - implementado na primeira parte.

Arquivos principais:

- `app/core/models.py`
- `app/core/services.py`

Problema:

- `bond_condition` e `anchorage_type` podem receber valores invalidos em chamadas diretas.
- O servico hoje pode gerar `KeyError` cru em vez de erro de validacao amigavel.

Acao:

- Validar se `bond_condition` e instancia de `BondCondition`.
- Validar se `anchorage_type` e instancia de `AnchorageType`.
- Converter erro para `ValidationError`.

Testes obrigatorios:

- [x] `bond_condition="ruim"` deve levantar `ValidationError`.
- [x] `anchorage_type="dobrado"` deve levantar `ValidationError`.

## 2. Regras de Calculo e Integridade

### 2.1 Fortalecer testes de borda de engenharia

Status: OK - testes de invalidos, limites, formulas e governancia adicionados. O caso "capacidade OK mas ancoragem reprovada" foi revisado e documentado como nao alcancavel pelo modelo atual, pois a capacidade por aderencia tambem depende da ancoragem disponivel.

Arquivo principal: `tests/test_services.py`

Adicionar testes para:

- [x] `loops_count = 0` e `loops_count < 0`.
- [x] `available_anchorage_cm = 0`.
- [x] `concrete_unit_weight_tf_m3 = 0`.
- [x] `strand_key` inexistente.
- [x] `inclination_deg = 0.1`, limite inferior aceito pelo core.
- [x] `inclination_deg = 90`, limite superior aceito.
- [x] `fckj_mpa = 50`, transicao da formula de `fctm`.
- [x] `fckj_mpa > 50`, uso da formula logaritmica.
- [x] Caso governado por aco.
- [x] Caso governado por aderencia.
- [x] Caso aprovado por capacidade mas reprovado por ancoragem revisado: nao alcancavel com o modelo atual.
- [x] Caso reprovado por capacidade mas aprovado por ancoragem.
- [x] Caso reprovado por ambos.

### 2.2 Conferir coerencia normativa

Status: OK - formulas e premissas principais foram alinhadas no README neste checkpoint.

Arquivos principais:

- `app/core/services.py`
- `README.md`

Acao:

- [x] Revisar as premissas adotadas para:
  - `ECJ_FACTOR = 0.9`
  - `GAMMA_C = 1.3`
  - `GAMMA_S = 1.15`
  - `ETA_P1_FOR_7_WIRE_STRAND = 1.2`
  - coeficientes de ancoragem
  - diferenca entre `fbpd_j` e `fbpd_28`
- [x] Confirmar que a memoria de calculo descreve exatamente as formulas implementadas.
- [x] Registrar no README que a ferramenta e preliminar e exige validacao do engenheiro responsavel.

## 3. Interface Grafica

### 3.1 Tornar `paintEvent` mais defensivo

Status: OK - implementado no segundo checkpoint.

Arquivo principal: `app/ui/sketch_widget.py`

Problema:

- O `QPainter` e finalizado com `p.end()`, mas nao ha `try/finally`.
- Uma excecao em rotina de desenho pode deixar o painter em estado inadequado.

Acao:

- Envolver desenho em `try/finally`.
- Garantir `p.end()` no `finally`.
- Manter o desenho simples, sem introduzir `QGraphicsScene` ou arquitetura nova.

Teste recomendado:

- [x] Renderizar `LiftingSketchWidget` em modo offscreen com dimensoes pequenas.
- [x] Renderizar com `loops_count=1`, `loops_count=20` e valor direto acima de 20.

### 3.2 Limitar parametros diretos do desenho

Status: OK - implementado no segundo checkpoint.

Arquivo principal: `app/ui/sketch_widget.py`

Problema:

- A UI limita `loops_count` a 20, mas `update_sketch` aceita valores arbitrarios se chamado diretamente.

Acao:

- [x] Aplicar limite superior em `update_sketch`, por exemplo `min(20, max(1, loops_count))`.
- [x] Manter coerencia com `QSpinBox` da janela principal.

### 3.3 Revisar robustez de sinais

Status: OK - conexoes seguem centralizadas no construtor e os atalhos agora ficam referenciados em `self._shortcuts`.

Arquivo principal: `app/ui/main_window.py`

Acao:

- [x] Manter conexoes feitas apenas uma vez no construtor.
- [x] Evitar chamadas repetidas a `_connect_auto_calculate`.
- [x] Verificar se atalhos criados em `_setup_shortcuts` permanecem vivos por terem `self` como parent.
- [x] Evitar desconectar sinais sem necessidade.

### 3.4 Remover calculo manual da interface

Status: OK - implementado neste checkpoint.

Arquivo principal: `app/ui/main_window.py`

Motivo:

- A aplicacao ja recalcula automaticamente quando os campos mudam.
- O botao manual duplicava o fluxo principal e podia sugerir que os resultados nao estavam atualizados.

Acao:

- [x] Remover o botao `Calcular Verificacao`.
- [x] Remover atalhos manuais de calculo (`F5` e `Ctrl+Enter`).
- [x] Manter atalhos apenas para navegacao entre abas.
- [x] Tratar validacao invalida como estado visivel da tela, sem modal.
- [x] Limpar o ultimo resultado valido ao detectar entrada invalida.
- [x] Atualizar testes e checklist manual.

## 4. Infraestrutura e Exportacao

### 4.1 Definir escopo real de SVG para a v1.0

Status: OK - SVG foi incluido no escopo e implementado neste checkpoint.

Situacao atual:

- [x] `app/infrastructure/svg_exporter.py` existe.
- [x] Ha teste fonte `tests/test_svg_exporter.py`.
- [x] A exportacao atual inclui TXT da memoria de calculo e SVG do desenho.

Decisao necessaria:

- [x] SVG definido como requisito da v1.0.
- [x] Exportador e testes implementados antes do release.

### 4.2 Implementar exportador SVG, se aprovado no escopo

Status: OK - implementado neste checkpoint.

Arquivo sugerido:

- `app/infrastructure/svg_exporter.py`

Requisitos:

- [x] Gerar SVG usando APIs seguras de XML, preferencialmente `xml.etree.ElementTree`.
- [x] Escapar caracteres especiais automaticamente.
- [x] Validar caminho de destino.
- [x] Capturar `OSError` e converter para erro amigavel quando chamado pela UI.
- [x] Nao misturar regra de negocio no exportador.
- [x] Aceitar dados estruturados simples do desenho ou resultado.

Testes obrigatorios:

- [x] Texto com acentos e caracteres especiais: `&`, `<`, `>`, `"`.
- [x] Caminho invalido deve falhar de forma previsivel.
- [x] SVG gerado deve ser XML valido.
- [x] Desenho com varias alcas deve gerar estrutura consistente.

## 5. Documentacao

### 5.1 Atualizar README

Status: OK - atualizado neste checkpoint.

Arquivo principal: `README.md`

Problemas atuais:

- A formula de `Ecj` documentada nao mostra o fator `0.9` usado no codigo.
- O README nao descreve claramente `Fck,28`.
- A diferenca entre `fbpd_j` e `fbpd_28` precisa ficar explicita.
- Os tipos de ancoragem e seus coeficientes precisam ser documentados.

Acao:

- [x] Atualizar lista de entradas.
- [x] Atualizar formulas.
- [x] Atualizar saidas.
- [x] Atualizar instrucoes de testes, se novos testes forem adicionados.
- [x] Documentar exportacao TXT e SVG.

### 5.2 Revisar versao do aplicativo

Status: OK - `APP_VERSION` passou a ser exibido no dialogo "Sobre" e foi alinhado para `1.0.0`.

Arquivo principal: `app/config/settings.py`

Acao:

- [x] Decidir se `APP_VERSION` sera exibido na UI ou removido.
- [x] Se mantido, exibir no dialogo "Sobre".
- [x] Ajustar versao final para `1.0.0` se este for o release oficial.

## 6. Limpeza de Codigo e Repositorio

### 6.1 Remover codigo nao usado

Status: OK - `_section_label` foi removido e `APP_VERSION` passou a ser usado.

Arquivos principais:

- `app/ui/main_window.py`
- `app/config/settings.py`

Itens identificados originalmente:

- `_section_label` nao e usado.
- `APP_VERSION` nao e usado.

Acao:

- [x] Remover `_section_label` se nao houver uso planejado imediato.
- [x] Usar ou remover `APP_VERSION`.

### 6.2 Limpar artefatos gerados

Status: PARCIAL - `.gitignore` foi criado e os caches Python versionados foram removidos do workspace. Depois dos testes, alguns `__pycache__` foram recriados localmente; a nova remocao foi bloqueada pelo limite de aprovacao da sessao. Dois diretorios temporarios antigos em `.tmp_test_outputs` tambem ficaram bloqueados pelo OneDrive e devem ser apagados manualmente se ainda aparecerem no Explorer.

Itens identificados:

- [x] Pastas `__pycache__`.
- [x] `.pytest_cache`.
- [ ] Imagens de screenshot soltas na raiz: mantidas por enquanto, pois podem ser evidencias/documentacao visual.
- [x] Arquivos `.pyc` em `tests`.
- [x] Possivel `test_svg_exporter.cpython-314.pyc` sem arquivo fonte correspondente.

Acao:

- [x] Remover artefatos gerados do controle de versao.
- [x] Criar ou atualizar `.gitignore` com:
  - [x] `__pycache__/`
  - [x] `*.pyc`
  - [x] `.pytest_cache/`
  - [x] `.venv/`
  - [x] `.tmp_test_outputs/`
  - [x] screenshots temporarios, se nao forem documentacao oficial.

## 7. Qualidade e Padroes

### 7.1 PEP 8 e tipagem

Status: OK - linhas Python acima de 99 caracteres foram quebradas e `paintEvent` recebeu tipo de evento.

Acao:

- [x] Quebrar linhas longas em `main_window.py`, `services.py` e `sketch_widget.py`.
- [x] Manter type hints em metodos publicos e privados relevantes.
- [x] Tipar `paintEvent` com o tipo correto de evento, se desejado.
- [x] Evitar imports longos em uma unica linha.

### 7.2 Tratamento de erros

Status: OK - validacoes e exportacoes usam erros especificos nos fluxos previstos.

Acao:

- [x] Erros de validacao devem sair como `ValidationError`.
- [x] Erros de arquivo devem sair como `OSError` na infraestrutura e mensagem amigavel na UI.
- [x] Evitar `KeyError`, `ValueError` e `TypeError` crus em fluxos esperados do usuario ou chamadas diretas ao core.

### 7.3 Smoke tests de release

Status: OK - fluxos principais foram cobertos por testes automatizados em modo offscreen.

Acao:

- [x] Abrir a janela principal em modo offscreen.
- [x] Validar calculo aprovado inicial.
- [x] Validar calculo reprovado sem modal.
- [x] Validar copia da memoria para clipboard.
- [x] Validar exportacao TXT com caminho contendo acentos, sem escrever arquivo real.
- [x] Validar exportacao SVG com caminho contendo acentos, sem escrever arquivo real.

### 7.4 Script de verificacao de release

Status: OK - script automatizado criado neste checkpoint.

Arquivo principal: `tools/release_check.py`

Acao:

- [x] Criar comando unico para checagens tecnicas antes do release.
- [x] Rodar suite de testes com `python -B`.
- [x] Rodar `git diff --check`.
- [x] Verificar linhas Python acima de 99 caracteres em `app/` e `tests/`.
- [x] Verificar marcadores de codigo pendente em `app/` e `tests/`.
- [x] Reportar `.pyc` e `screenshot_*.png` rastreados como avisos em modo normal.
- [x] Disponibilizar modo `--strict` para falhar enquanto artefatos rastreados existirem.

## 8. Checklist de Release

Antes de fechar a versao 1.0:

- [x] Validacoes criticas implementadas no core.
- [x] Testes de valores negativos, zero, `NaN` e infinitos adicionados.
- [x] Testes de enums invalidos adicionados.
- [x] Testes de borda de inclinacao, fck e ancoragem adicionados.
- [x] `paintEvent` protegido com finalizacao garantida do `QPainter`.
- [x] `update_sketch` limitado ao intervalo suportado pela UI.
- [x] Decisao tomada sobre exportacao SVG.
- [x] SVG implementado e testado, se fizer parte da v1.0.
- [x] README atualizado com formulas reais e escopo real.
- [x] `APP_VERSION` usado ou removido.
- [x] Codigo morto removido.
- [ ] Artefatos gerados removidos ou ignorados. Parcial: screenshots e dois temporarios bloqueados ainda exigem decisao/acao manual.
- [x] `python -m unittest discover -s tests` executado com sucesso.
- [x] `python -m py_compile` executado nos modulos principais.
- [x] `python -B tools/release_check.py` executado com sucesso em modo normal.
- [ ] `python -B tools/release_check.py --strict` sem falhas. Pendente ate remover `.pyc`/screenshots rastreados ou decidir manter os screenshots oficialmente.
- [ ] Aplicacao aberta em ambiente Windows limpo com Python 3.11+. Automatizado em offscreen, pendente validacao manual em ambiente limpo.
- [ ] Fluxo manual validado: alterar dados, recalculo automatico aprovado/reprovado, copiar memoria e exportar TXT. Automatizado em offscreen, pendente validacao manual.
- [ ] Teste manual com caminho de arquivo contendo acentos. Automatizado com mocks, pendente validacao manual gravando arquivo real.
- [ ] Revisao final por engenheiro responsavel antes de uso operacional.

## 9. Estado Release Candidate

Status: RC tecnico quase fechado. As correcoes de codigo, testes automatizados, documentacao tecnica e exportacao SVG foram implementadas. O que resta antes de declarar release final e operacional/manual, nao uma pendencia conhecida de regra de negocio.

Validado automaticamente:

- [x] Suite de testes com 57 testes passando.
- [x] `git diff --check` sem erros.
- [x] `python -B tools/release_check.py` sem falhas em modo normal.
- [x] Smoke test da janela principal em modo offscreen.
- [x] Calculo aprovado inicial.
- [x] Calculo reprovado.
- [x] Copia da memoria para clipboard.
- [x] Exportacao TXT via fluxo da UI com caminho acentuado mockado.
- [x] Exportacao SVG via fluxo da UI com caminho acentuado mockado.
- [x] Exportador SVG gera XML valido e escapa caracteres especiais.
- [x] Nao ha `TODO`, `FIXME`, `except Exception` ou `NotImplemented` nos arquivos-fonte.
- [x] Nao ha linhas Python acima de 99 caracteres em `app/` e `tests/`.
- [x] `RELEASE_NOTES.md` criado para a versao 1.0.0.
- [x] `CHECKLIST_VALIDACAO_MANUAL.md` criado para orientar o fechamento manual.

Pendencias manuais antes do release final:

- [ ] Executar `CHECKLIST_VALIDACAO_MANUAL.md` em ambiente Windows limpo.
- [ ] Remover do controle de versao todos os `.pyc` atualmente rastreados por Git.
- [ ] Apagar manualmente os diretorios antigos bloqueados em `.tmp_test_outputs`, se ainda existirem.
- [ ] Decidir se os `screenshot_*.png` ficam como evidencia/documentacao visual ou se devem sair do repositorio.
- [ ] Rodar `python -B tools/release_check.py --strict` apos a limpeza dos artefatos rastreados.
- [ ] Executar em venv limpo no Windows com `pip install -r requirements.txt`.
- [ ] Abrir a aplicacao visivelmente com `python app/main.py`.
- [ ] Validar manualmente: caso aprovado, caso reprovado, copia da memoria, exportacao TXT real e exportacao SVG real.
- [ ] Validar gravacao real em caminho com acentos.
- [ ] Revisao final por engenheiro responsavel.

Manifesto de limpeza Git:

- `.gitignore` cobre novos `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.tmp_test_outputs/` e `screenshot_*.png`.
- Atualmente existem 18 arquivos `.pyc` rastreados por Git que devem sair do controle de versao.
- Atualmente existem 11 `screenshot_*.png` rastreados por Git; decidir se devem permanecer como evidencia visual ou sair do repositorio.
- Os arquivos `.pyc` rastreados sao:
  - `app/__pycache__/__init__.cpython-314.pyc`
  - `app/__pycache__/main.cpython-314.pyc`
  - `app/config/__pycache__/__init__.cpython-314.pyc`
  - `app/config/__pycache__/settings.cpython-314.pyc`
  - `app/core/__pycache__/__init__.cpython-314.pyc`
  - `app/core/__pycache__/exceptions.cpython-314.pyc`
  - `app/core/__pycache__/models.cpython-314.pyc`
  - `app/core/__pycache__/services.cpython-314.pyc`
  - `app/infrastructure/__pycache__/__init__.cpython-314.pyc`
  - `app/infrastructure/__pycache__/svg_exporter.cpython-314.pyc`
  - `app/ui/__pycache__/__init__.cpython-314.pyc`
  - `app/ui/__pycache__/main_window.cpython-314.pyc`
  - `app/ui/__pycache__/sketch_widget.cpython-314.pyc`
  - `app/ui/__pycache__/styles.cpython-314.pyc`
  - `tests/__pycache__/test_services.cpython-314-pytest-9.0.3.pyc`
  - `tests/__pycache__/test_services.cpython-314.pyc`
  - `tests/__pycache__/test_sketch_widget.cpython-314.pyc`
  - `tests/__pycache__/test_svg_exporter.cpython-314.pyc`
- Os screenshots rastreados sao:
  - `screenshot_final.png`
  - `screenshot_fix.png`
  - `screenshot_fix2.png`
  - `screenshot_fix3.png`
  - `screenshot_fix4.png`
  - `screenshot_janela.png`
  - `screenshot_main.png`
  - `screenshot_memory.png`
  - `screenshot_v5.png`
  - `screenshot_v6.png`
  - `screenshot_v7.png`

## Ordem Recomendada de Execucao

1. Corrigir validacoes do core.
2. Adicionar testes dos casos criticos.
3. Ajustar robustez do widget de desenho.
4. Resolver decisao sobre SVG.
5. Atualizar README.
6. Remover codigo morto e artefatos gerados.
7. Executar suite completa e smoke test da interface.
