# Painel de Especialistas UI/UX — Verificador de Içamento

## Screenshots analisados

![Aba Verificação](C:\Users\guilherme.nardelli\.gemini\antigravity\brain\aabe7965-f755-4d94-ae06-8bd7364f6179\artifacts\screenshot_main.png)

![Aba Memória de Cálculo](C:\Users\guilherme.nardelli\.gemini\antigravity\brain\aabe7965-f755-4d94-ae06-8bd7364f6179\artifacts\screenshot_memory.png)

---

## A. Resumo Executivo

**Nota geral: 6,5 / 10**

A interface é funcional e bem organizada para um MVP de engenharia, com boa separação entrada/resultado e representação gráfica dinâmica. Porém há oportunidades significativas de melhoria em hierarquia visual, acessibilidade, feedback contextual e usabilidade dos formulários.

### 5 Maiores Problemas

| # | Problema | Impacto |
|---|---------|---------|
| 1 | **12 campos de entrada numa lista vertical sem agrupamento semântico** — mistura dados da peça, do aço, da ancoragem e coeficientes | Carga cognitiva alta; usuário não sabe por onde começar |
| 2 | **Resultado cortado** — só mostra "Cargas" e início de "Propriedades"; seções Verificações e Indicadores ficam escondidas abaixo do scroll | Informação mais crítica (aprovado/reprovado por quê) fica invisível |
| 3 | **Sem tooltips, sem ajuda contextual, sem unidades visíveis nos labels** — "βa (ampl. dinâmica)" é críptico para quem não é projetista sênior | Barreira para novos usuários |
| 4 | **Sem cálculo automático (live)** — precisa clicar "Calcular verificação" a cada alteração | Fluxo lento; engenheiros querem feedback imediato ao alterar parâmetros |
| 5 | **Sem status bar, sem atalhos de teclado, sem ações de menu** — app parece incompleto para desktop profissional | Impressão de ferramenta amadora |

### 5 Maiores Oportunidades

| # | Oportunidade | Resultado esperado |
|---|-------------|-------------------|
| 1 | **Agrupar inputs em 3-4 sub-grupos** (Peça, Cordoalha, Ancoragem, Coeficientes) | Formulário escaneável em 2 segundos |
| 2 | **Cálculo reativo (auto-calculate on change)** | Feedback instantâneo; elimina botão como barreira |
| 3 | **Reorganizar resultado com resumo visual no topo** (gauges/barras para FS e utilização) | Status aprovado/reprovado compreensível de relance |
| 4 | **Adicionar QMenuBar + QStatusBar + atalhos** | App profissional; produtividade com teclado |
| 5 | **Tooltips técnicos com referências normativas** em cada campo | Auto-documentação; reduz erros de preenchimento |

---

## B. Diagnóstico por Tela/Componente

### B1. Aba "Verificação" — Painel de Entrada

| Aspecto | Avaliação |
|---------|-----------|
| **Bom** | QFormLayout limpo; labels à esquerda e campos à direita; sufixos de unidade nos spinboxes; botão de ação claro |
| **Ruim** | 12 campos em lista corrida sem separação visual; não há agrupamento semântico; labels sem acentos ("Inclinacao", "icamento"); campos como βa e γn sem explicação; sem tooltips |
| **Impacto** | Engenheiro precisa ler todos os 12 campos para entender o contexto; erro de preenchimento provável em βa/γn |
| **Recomendação** | Dividir em QGroupBox internos: "Concreto" (fck,j + fck,28), "Peça" (volume + peso esp.), "Cordoalha e Içamento" (cordoalha + inclinação + alças), "Ancoragem" (anc. disponível + tipo + aderência), "Coeficientes" (βa + γn) |
| **Prioridade** | **Alta** |
| **Esforço** | Pequeno |

### B2. Aba "Verificação" — Painel de Resultado

| Aspecto | Avaliação |
|---------|-----------|
| **Bom** | Banner APROVADA/REPROVADA com cores claras; seções com labels de seção bold; campos com cor condicional (verde/vermelho) |
| **Ruim** | Resultado fica cortado — só cargas e início de propriedades visível; link "Memória completa..." é sutil demais; seção "Indicadores" (a mais importante) fica escondida; muitos campos de resultado intermediário (Ec,j, fctm) ocupam espaço visual de campos decisórios |
| **Impacto** | Usuário vê "APROVADA" mas não vê imediatamente o FS, a taxa de utilização e a mobilização do aço — dados que precisa para tomar decisão |
| **Recomendação** | (1) Mover Indicadores para logo abaixo do banner; (2) Colapsar "Propriedades dos materiais" em um QGroupBox colapsável; (3) Usar barras de progresso visuais para utilização e FS |
| **Prioridade** | **Alta** |
| **Esforço** | Médio |

### B3. Representação Gráfica (Sketch)

| Aspecto | Avaliação |
|---------|-----------|
| **Bom** | Desenho dinâmico reativo a parâmetros; mostra alças, ancoragem, inclinação; labels "CONCRETO", tipo de ancoragem, nº alças |
| **Ruim** | Desenho pequeno (ocupa ~35% da tela); não mostra cotas/dimensões; não destaca visualmente ancoragem insuficiente; cores do strand fixas (sempre verde mesmo se reprovado) |
| **Impacto** | O sketch é informativo mas não é diagnóstico — não ajuda a entender *por que* reprovou |
| **Recomendação** | (1) Mostrar cota de ancoragem disponível vs. necessária; (2) Colorir strand em vermelho quando ancoragem insuficiente; (3) Permitir redimensionar via QSplitter |
| **Prioridade** | Média |
| **Esforço** | Médio |

### B4. Aba "Memória de Cálculo"

| Aspecto | Avaliação |
|---------|-----------|
| **Bom** | Conteúdo técnico completo com fórmulas e substituição numérica; formatação plain-text clara; referências normativas |
| **Ruim** | Sem botão de exportar/copiar; sem formatação rica (poderia usar HTML); sem cabeçalho com data/hora; sem numeração de versão ou identificação da peça |
| **Impacto** | Engenheiro precisa selecionar tudo manualmente para colar em relatório |
| **Recomendação** | (1) Botão "Copiar" e "Exportar .txt"; (2) Adicionar cabeçalho com timestamp; (3) Campo opcional "Identificação da peça" nos inputs |
| **Prioridade** | Média |
| **Esforço** | Pequeno |

---

## C. Avaliação pelas Heurísticas de Nielsen

| Heurística | Evidência | Problema | Recomendação |
|-----------|-----------|----------|-------------|
| **1. Visibilidade do estado** | Banner APROVADA/REPROVADA visível | Indicadores (FS, utilização) ficam abaixo do scroll | Mover indicadores para cima; adicionar QStatusBar com resumo |
| **2. Compatibilidade com mundo real** | Labels usam termos técnicos corretos (fck,j, fbpd) | Falta de acentos ("Verificacao", "icamento"); βa sem explicação para leigos | Acentuar labels; adicionar tooltips com definição |
| **3. Controle e liberdade** | Botão calcular permite recalcular | Sem undo/redo; sem "Valores padrão"; sem "Limpar" | Adicionar "Restaurar padrões" e considerar auto-cálculo |
| **4. Consistência e padrões** | Estilo visual consistente (cores, fontes) | Resultado usa QLineEdit readonly (parece editável); falta ícones nos botões | Usar QLabel para resultados; ou estilizar QLineEdit como badge |
| **5. Prevenção de erros** | QDoubleSpinBox com ranges definidos | Sem validação visual inline (campo fica normal mesmo se fck28 < fckj); erro só aparece em QMessageBox | Validar inline com borda vermelha no campo; tooltip com regra |
| **6. Reconhecimento > memória** | Labels presentes em cada campo | Sem tooltips; coeficientes βa/γn sem contexto; unidades só no sufixo | Tooltips com definição + referência normativa |
| **7. Flexibilidade e eficiência** | Auto-calcula no startup | Sem atalhos; sem menu; sem tecla Enter para calcular | F5 ou Ctrl+Enter para calcular; Ctrl+C na memória |
| **8. Design estético e minimalista** | Visual limpo, tema claro, tipografia Segoe UI | Formulário muito longo; resultado com excesso de dados intermediários | Colapsar seções secundárias; destacar indicadores |
| **9. Ajuda ao diagnosticar erros** | Banner mostra "capacidade insuficiente" / "ancoragem insuficiente" | Não diz o que fazer para corrigir | Adicionar sugestão: "Aumente a ancoragem de X para Y cm" |
| **10. Documentação e ajuda** | Memória de cálculo disponível | Sem menu Ajuda; sem referência à norma na UI; sem sobre/versão | QMenuBar com Ajuda > Sobre; tooltip com §9.3.2.2 |

---

## D. Avaliação de Acessibilidade

| Critério | Status | Detalhe | Recomendação PySide6 |
|----------|--------|---------|---------------------|
| **Contraste** | ⚠️ | Labels #334155 sobre #f8fafc = ratio ~7:1 (OK). Mas link "Memória completa" #4b5563 com font-size 9pt = ~5:1 (limítrofe) | Aumentar para 9.5pt ou escurecer cor do link |
| **Labels visíveis** | ✅ | Todos os campos têm labels via QFormLayout | — |
| **Ordem de tabulação** | ⚠️ | Não definida explicitamente; depende da ordem de criação | Definir `setTabOrder()` explícito |
| **Foco visível** | ⚠️ | CSS define border azul no `:focus`, mas resultado usa `NoFocus` policy | OK para readonly; verificar que inputs focáveis são visíveis |
| **Navegação sem mouse** | ❌ | Sem atalhos; sem QMenuBar; sem QAction; Tab funciona mas sem mnemônicos | Adicionar `&` nos labels ou QAction com shortcut |
| **Leitores de tela** | ❌ | Nenhum `setAccessibleName()` ou `setAccessibleDescription()` definido | Adicionar accessibleName em todos os inputs e resultados |
| **Mensagens de erro** | ⚠️ | QMessageBox.warning — acessível mas interruptivo | OK, mas adicionar validação inline antes do modal |
| **Tamanho dos controles** | ✅ | Padding 6-8px; altura adequada | — |
| **Estados (disabled/loading)** | ❌ | Sem estado de loading; sem disabled durante cálculo | Para cálculos futuros pesados: QProgressDialog |
| **Recomendação PySide6** | — | — | `widget.setAccessibleName("Resistência do concreto na idade do içamento")` em cada input |

---

## E. Plano de Melhoria Priorizado

### Fase 1 — Correções Rápidas de Alto Impacto (1-3 dias)

| # | Tarefa | Motivo | Resultado | Como em PySide6 | Critério de Aceite |
|---|--------|--------|-----------|-----------------|-------------------|
| 1.1 | **Acentuar todos os textos** | "Verificacao" → "Verificação"; "icamento" → "Içamento" | Profissionalismo | Alterar strings em main_window.py e settings.py | Nenhum texto sem acento |
| 1.2 | **Agrupar inputs em sub-seções** | 12 campos corridos → 4 grupos semânticos | Escaneabilidade | Criar 4 QGroupBox dentro do grupo "Dados de entrada" | Cada grupo tem título e ≤4 campos |
| 1.3 | **Mover Indicadores para cima do resultado** | FS e utilização são as info mais importantes | Decisão imediata | Reordenar seções em `_build_result_panel` | FS e utilização visíveis sem scroll |
| 1.4 | **Adicionar tooltips em todos os inputs** | Contexto técnico sem manual | Auto-documentação | `self.fckj_input.setToolTip("Resistência...")` | Cada input tem tooltip com definição |
| 1.5 | **Auto-cálculo reativo** | Eliminar fricção do botão | Feedback imediato | Conectar `valueChanged`/`currentIndexChanged` de todos inputs ao `_on_calculate` | Resultado atualiza ao mudar qualquer valor |
| 1.6 | **Adicionar QStatusBar** | Feedback persistente + versão | App profissional | `self.statusBar().showMessage(...)` | Status bar mostra "Aprovado FS=X.XX" |
| 1.7 | **Atalho Enter/F5 para calcular** | Produtividade com teclado | Eficiência | `QShortcut(QKeySequence("F5"), self, self._on_calculate)` | F5 recalcula |
| 1.8 | **Botão "Copiar" na memória de cálculo** | Exportação rápida | Produtividade | `QPushButton` que faz `QApplication.clipboard().setText(...)` | Botão copia texto para clipboard |

### Fase 2 — Refatoração Visual e Fluxo (1-2 semanas)

| # | Tarefa | Motivo | Resultado | Como em PySide6 | Critério de Aceite |
|---|--------|--------|-----------|-----------------|-------------------|
| 2.1 | **QSplitter horizontal** entre inputs+resultado (cima) e sketch (baixo) | Usuário controla área visual | Responsividade | `QSplitter(Qt.Vertical)` substituindo o layout fixo | Sketch redimensionável |
| 2.2 | **Barras visuais para FS e Utilização** | Dados numéricos são menos imediatos que visuais | Compreensão instantânea | QProgressBar estilizado ou widget customizado | Barra mostra % com cor condicional |
| 2.3 | **QMenuBar** (Arquivo, Ferramentas, Ajuda) | Completude de app desktop | Profissional | Exportar memória, Restaurar padrões, Sobre | Menu funcional com 3+ itens |
| 2.4 | **Validação inline** nos campos | Erro antes de calcular | Prevenção de erro | Conectar `valueChanged` a método que colore borda se fck28 < fckj | Campo com borda vermelha + tooltip de erro |
| 2.5 | **Sketch diagnóstico** | Colorir vermelho se ancoragem insuficiente | Feedback visual | Alterar `_STRAND_COLOR` condicionalmente com base no resultado | Strand vermelho quando reprova |
| 2.6 | **Cotas no sketch** | Mostrar dimensões de ancoragem | Informação quantitativa visual | Desenhar linhas de cota com texto cm | Cota de ancoragem disponível e necessária visíveis |
| 2.7 | **Campo "Identificação da peça"** opcional | Rastreabilidade no relatório | Memória identificada | QLineEdit no topo dos inputs | Texto aparece no cabeçalho da memória |
| 2.8 | **Mensagem de reprovação com sugestão** | Ajudar a corrigir, não só apontar erro | Orientação ativa | Calcular ancoragem mínima ou nº mínimo de alças e exibir no banner | "Reprovada: aumente ancoragem para ≥ 72.5 cm" |

### Fase 3 — Evolução Avançada (futuro)

| # | Tarefa | Motivo | Resultado | Como em PySide6 | Critério de Aceite |
|---|--------|--------|-----------|-----------------|-------------------|
| 3.1 | **accessibleName/Description** em todos os widgets | Acessibilidade para leitores de tela | WCAG compliance | `setAccessibleName()` em cada input e resultado | Verificável com Narrator/NVDA |
| 3.2 | **Exportar memória em PDF** | Documento formal para relatório | Produtividade | QPrinter + QPainter ou reportlab | Botão gera PDF formatado |
| 3.3 | **Salvar/Carregar configuração** | Reutilizar dados entre sessões | Eficiência | JSON com QFileDialog | Salvar e abrir dados da peça |
| 3.4 | **Tema escuro opcional** | Preferência do usuário | Conforto visual | Variantes em styles.py + QAction toggle | Menu Ferramentas > Tema claro/escuro |
| 3.5 | **Testes com usuários** | Validar suposições do painel | Melhoria baseada em dados | Sessão de 15min com 3 engenheiros | Relatório com 5+ insights acionáveis |

