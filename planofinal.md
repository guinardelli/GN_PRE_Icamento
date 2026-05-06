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

Arquivos principais:

- `app/core/services.py`
- `README.md`

Acao:

- Revisar as premissas adotadas para:
  - `ECJ_FACTOR = 0.9`
  - `GAMMA_C = 1.3`
  - `GAMMA_S = 1.15`
  - `ETA_P1_FOR_7_WIRE_STRAND = 1.2`
  - coeficientes de ancoragem
  - diferenca entre `fbpd_j` e `fbpd_28`
- Confirmar que a memoria de calculo descreve exatamente as formulas implementadas.
- Registrar no README que a ferramenta e preliminar e exige validacao do engenheiro responsavel.

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

Arquivo principal: `app/ui/main_window.py`

Acao:

- Manter conexoes feitas apenas uma vez no construtor.
- Evitar chamadas repetidas a `_connect_auto_calculate`.
- Verificar se atalhos criados em `_setup_shortcuts` permanecem vivos por terem `self` como parent.
- Evitar desconectar sinais sem necessidade.

## 4. Infraestrutura e Exportacao

### 4.1 Definir escopo real de SVG para a v1.0

Situacao atual:

- `app/infrastructure/svg_exporter.py` nao existe.
- Nao ha teste fonte `tests/test_svg_exporter.py`.
- A exportacao atual e apenas TXT da memoria de calculo.

Decisao necessaria:

- Se SVG nao for requisito da v1.0, remover mencoes pendentes e documentar apenas exportacao TXT.
- Se SVG for requisito da v1.0, implementar exportador e testes antes do release.

### 4.2 Implementar exportador SVG, se aprovado no escopo

Arquivo sugerido:

- `app/infrastructure/svg_exporter.py`

Requisitos:

- Gerar SVG usando APIs seguras de XML, preferencialmente `xml.etree.ElementTree`.
- Escapar caracteres especiais automaticamente.
- Validar caminho de destino.
- Capturar `OSError` e converter para erro amigavel quando chamado pela UI.
- Nao misturar regra de negocio no exportador.
- Aceitar dados estruturados simples do desenho ou resultado.

Testes obrigatorios:

- Texto com acentos e caracteres especiais: `&`, `<`, `>`, `"`.
- Caminho invalido deve falhar de forma previsivel.
- SVG gerado deve ser XML valido.
- Desenho com varias alcas deve gerar estrutura consistente.

## 5. Documentacao

### 5.1 Atualizar README

Arquivo principal: `README.md`

Problemas atuais:

- A formula de `Ecj` documentada nao mostra o fator `0.9` usado no codigo.
- O README nao descreve claramente `Fck,28`.
- A diferenca entre `fbpd_j` e `fbpd_28` precisa ficar explicita.
- Os tipos de ancoragem e seus coeficientes precisam ser documentados.

Acao:

- Atualizar lista de entradas.
- Atualizar formulas.
- Atualizar saidas.
- Atualizar instrucoes de testes, se novos testes forem adicionados.
- Documentar exportacao TXT e, se implementado, SVG.

### 5.2 Revisar versao do aplicativo

Arquivo principal: `app/config/settings.py`

Acao:

- Decidir se `APP_VERSION` sera exibido na UI ou removido.
- Se mantido, exibir no dialogo "Sobre".
- Ajustar versao final para `1.0.0` se este for o release oficial.

## 6. Limpeza de Codigo e Repositorio

### 6.1 Remover codigo nao usado

Arquivos principais:

- `app/ui/main_window.py`
- `app/config/settings.py`

Itens identificados:

- `_section_label` nao e usado.
- `APP_VERSION` nao e usado.

Acao:

- Remover `_section_label` se nao houver uso planejado imediato.
- Usar ou remover `APP_VERSION`.

### 6.2 Limpar artefatos gerados

Itens identificados:

- Pastas `__pycache__`.
- `.pytest_cache`.
- Imagens de screenshot soltas na raiz.
- Arquivos `.pyc` em `tests`.
- Possivel `test_svg_exporter.cpython-314.pyc` sem arquivo fonte correspondente.

Acao:

- Remover artefatos gerados do controle de versao.
- Criar ou atualizar `.gitignore` com:
  - `__pycache__/`
  - `*.pyc`
  - `.pytest_cache/`
  - `.venv/`
  - `.tmp_test_outputs/`
  - screenshots temporarios, se nao forem documentacao oficial.

## 7. Qualidade e Padroes

### 7.1 PEP 8 e tipagem

Acao:

- Quebrar linhas longas em `main_window.py`, `services.py` e `sketch_widget.py`.
- Manter type hints em metodos publicos e privados relevantes.
- Tipar `paintEvent` com o tipo correto de evento, se desejado.
- Evitar imports longos em uma unica linha.

### 7.2 Tratamento de erros

Acao:

- Erros de validacao devem sair como `ValidationError`.
- Erros de arquivo devem sair como `OSError` na infraestrutura e mensagem amigavel na UI.
- Evitar `KeyError`, `ValueError` e `TypeError` crus em fluxos esperados do usuario ou chamadas diretas ao core.

## 8. Checklist de Release

Antes de fechar a versao 1.0:

- [x] Validacoes criticas implementadas no core.
- [x] Testes de valores negativos, zero, `NaN` e infinitos adicionados.
- [x] Testes de enums invalidos adicionados.
- [x] Testes de borda de inclinacao, fck e ancoragem adicionados.
- [x] `paintEvent` protegido com finalizacao garantida do `QPainter`.
- [x] `update_sketch` limitado ao intervalo suportado pela UI.
- [ ] Decisao tomada sobre exportacao SVG.
- [ ] SVG implementado e testado, se fizer parte da v1.0.
- [ ] README atualizado com formulas reais e escopo real.
- [ ] `APP_VERSION` usado ou removido.
- [ ] Codigo morto removido.
- [ ] Artefatos gerados removidos ou ignorados.
- [x] `python -m unittest discover -s tests` executado com sucesso.
- [x] `python -m py_compile` executado nos modulos principais.
- [ ] Aplicacao aberta em ambiente Windows limpo com Python 3.11+.
- [ ] Fluxo manual validado: calcular aprovado, calcular reprovado, copiar memoria e exportar TXT.
- [ ] Teste manual com caminho de arquivo contendo acentos.
- [ ] Revisao final por engenheiro responsavel antes de uso operacional.

## Ordem Recomendada de Execucao

1. Corrigir validacoes do core.
2. Adicionar testes dos casos criticos.
3. Ajustar robustez do widget de desenho.
4. Resolver decisao sobre SVG.
5. Atualizar README.
6. Remover codigo morto e artefatos gerados.
7. Executar suite completa e smoke test da interface.
