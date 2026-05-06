# Painel de Especialistas UI/UX — Parte 2

## F. Sugestões Técnicas em PySide6

### F1. Agrupamento de Inputs com QGroupBox Internos

```python
def _build_input_group(self) -> QGroupBox:
    group = QGroupBox("Dados de entrada")
    layout = QVBoxLayout(group)
    layout.setSpacing(6)

    # --- Sub-grupo: Concreto ---
    concrete_group = QGroupBox("Concreto")
    concrete_form = QFormLayout(concrete_group)
    concrete_form.addRow("Fck,j (içamento):", self.fckj_input)
    concrete_form.addRow("Fck (28 dias):", self.fck_28_input)
    layout.addWidget(concrete_group)

    # --- Sub-grupo: Peça ---
    piece_group = QGroupBox("Peça")
    piece_form = QFormLayout(piece_group)
    piece_form.addRow("Volume:", self.volume_input)
    piece_form.addRow("Peso específico:", self.unit_weight_input)
    layout.addWidget(piece_group)

    # --- Sub-grupo: Cordoalha e Içamento ---
    strand_group = QGroupBox("Cordoalha e Içamento")
    strand_form = QFormLayout(strand_group)
    strand_form.addRow("Cordoalha:", self.strand_input)
    strand_form.addRow("Inclinação:", self.inclination_input)
    strand_form.addRow("Quantidade de alças:", self.loops_input)
    layout.addWidget(strand_group)

    # --- Sub-grupo: Ancoragem ---
    anc_group = QGroupBox("Ancoragem")
    anc_form = QFormLayout(anc_group)
    anc_form.addRow("Comprimento disponível:", self.anchorage_input)
    anc_form.addRow("Tipo de ancoragem:", self.anchorage_type_input)
    anc_form.addRow("Condição de aderência:", self.bond_input)
    layout.addWidget(anc_group)

    # --- Sub-grupo: Coeficientes ---
    coeff_group = QGroupBox("Coeficientes")
    coeff_form = QFormLayout(coeff_group)
    coeff_form.addRow("βa (amplificação dinâmica):", self.beta_a_input)
    coeff_form.addRow("γn (majoração):", self.gamma_n_input)
    layout.addWidget(coeff_group)

    # Botão principal
    layout.addWidget(calculate_button)
    layout.addStretch(1)
    return group
```

### F2. Auto-cálculo Reativo

```python
def _connect_auto_calculate(self) -> None:
    """Conecta todos os inputs ao recálculo automático."""
    for spinbox in (
        self.fckj_input, self.fck_28_input, self.volume_input,
        self.unit_weight_input, self.inclination_input,
        self.anchorage_input, self.beta_a_input, self.gamma_n_input,
    ):
        spinbox.valueChanged.connect(self._on_calculate)

    self.loops_input.valueChanged.connect(self._on_calculate)
    self.strand_input.currentIndexChanged.connect(self._on_calculate)
    self.bond_input.currentIndexChanged.connect(self._on_calculate)
    self.anchorage_type_input.currentIndexChanged.connect(self._on_calculate)
```

### F3. QStatusBar

```python
def _build_ui(self) -> None:
    # ... (código existente) ...
    
    # Adicionar status bar
    self.status_bar = self.statusBar()
    self.status_bar.showMessage("Pronto")

def _on_calculate(self) -> None:
    # ... (código existente) ...
    if is_approved:
        self.status_bar.showMessage(
            f"✔ Aprovado — FS = {result.safety_factor:.2f} | "
            f"Utilização = {result.utilization_ratio:.1%}"
        )
    else:
        self.status_bar.showMessage(
            f"✘ Reprovado — {', '.join(failures)}"
        )
```

### F4. Atalhos de Teclado

```python
from PySide6.QtGui import QKeySequence, QShortcut

def _setup_shortcuts(self) -> None:
    QShortcut(QKeySequence("F5"), self, self._on_calculate)
    QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.tabs.setCurrentIndex(0))
    QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.tabs.setCurrentIndex(1))
```

### F5. Tooltips Técnicos

```python
self.fckj_input.setToolTip(
    "Resistência característica do concreto na idade do içamento.\n"
    "Valor típico: 15–25 MPa para desmoldagem precoce.\n"
    "Referência: NBR 6118:2023 §12.3.3"
)
self.beta_a_input.setToolTip(
    "Coeficiente de amplificação dinâmica (NBR 9062).\n"
    "Valor padrão: 3,0 para içamento com guincho.\n"
    "Valores menores exigem justificativa técnica."
)
self.gamma_n_input.setToolTip(
    "Coeficiente de majoração adicional (NBR 9062).\n"
    "Valor padrão: 1,30.\n"
    "Majoração total = βa × γn"
)
```

### F6. Acessibilidade

```python
self.fckj_input.setAccessibleName("Resistência do concreto na idade do içamento em MPa")
self.fck_28_input.setAccessibleName("Resistência do concreto aos 28 dias em MPa")
self.volume_input.setAccessibleName("Volume da peça em metros cúbicos")
self.anchorage_input.setAccessibleName("Comprimento de ancoragem disponível em centímetros")
self.strand_input.setAccessibleName("Tipo de cordoalha de protensão")
```

### F7. Botão Copiar na Memória

```python
def _build_memory_tab(self) -> QWidget:
    tab = QWidget()
    layout = QVBoxLayout(tab)

    toolbar = QHBoxLayout()
    copy_btn = QPushButton("📋 Copiar memória")
    copy_btn.clicked.connect(self._copy_memory)
    toolbar.addWidget(copy_btn)
    toolbar.addStretch()
    layout.addLayout(toolbar)

    self.memory_text = QTextEdit()
    self.memory_text.setReadOnly(True)
    layout.addWidget(self.memory_text)
    return tab

def _copy_memory(self) -> None:
    text = self.memory_text.toPlainText()
    if text:
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage("Memória copiada para a área de transferência", 3000)
```

### F8. Validação Inline (fck28 < fckj)

```python
def _validate_fck_relationship(self) -> None:
    if self.fck_28_input.value() < self.fckj_input.value():
        self.fck_28_input.setStyleSheet(
            "QDoubleSpinBox { border: 2px solid #dc2626; background: #fef2f2; }"
        )
        self.fck_28_input.setToolTip("⚠ Fck(28) deve ser ≥ Fck,j")
    else:
        self.fck_28_input.setStyleSheet("")  # Reset to default
        self.fck_28_input.setToolTip("Resistência do concreto aos 28 dias")
```

---

## G. Redesign Textual

### Labels (Antes → Depois)

| Antes | Depois | Motivo |
|-------|--------|--------|
| `Fck,j (icamento):` | `Fck,j (içamento):` | Acentuação |
| `Fck (28 dias):` | `Fck,28 (28 dias):` | Consistência com notação técnica |
| `Volume da peca:` | `Volume da peça:` | Acentuação |
| `Peso especifico:` | `Peso específico:` | Acentuação |
| `Inclinacao:` | `Inclinação da alça:` | Clareza + acentuação |
| `Ancoragem disponivel:` | `Comprimento de ancoragem:` | Mais preciso tecnicamente |
| `Aderencia:` | `Condição de aderência:` | Completude |
| `Quantidade de alcas:` | `Número de alças:` | Mais natural |
| `βa (ampl. dinamica):` | `βa (amplificação dinâmica):` | Acentuação + completude |
| `γn (majoracao):` | `γn (majoração):` | Acentuação |

### Títulos de Tabs

| Antes | Depois |
|-------|--------|
| `Verificacao` | `Verificação` |
| `Memoria de calculo` | `Memória de Cálculo` |

### Títulos de Seções

| Antes | Depois |
|-------|--------|
| `Dados de entrada` | `Dados de Entrada` |
| `Resultado` | `Resultado da Verificação` |
| `Representacao grafica` | `Representação Gráfica` |

### Botões

| Antes | Depois |
|-------|--------|
| `Calcular verificacao` | `Calcular Verificação` |
| *(não existe)* | `📋 Copiar Memória` |
| *(não existe)* | `Restaurar Padrões` |

### Mensagens de Status

| Antes | Depois |
|-------|--------|
| `VERIFICACAO APROVADA` | `✔ VERIFICAÇÃO APROVADA` |
| `VERIFICACAO REPROVADA: capacidade insuficiente` | `✘ VERIFICAÇÃO REPROVADA — Capacidade insuficiente` |
| `VERIFICACAO REPROVADA: ancoragem insuficiente` | `✘ VERIFICAÇÃO REPROVADA — Ancoragem insuficiente. Necessário ≥ {X} cm (disponível: {Y} cm)` |

### Tooltips Sugeridos

| Campo | Tooltip |
|-------|---------|
| Fck,j | "Resistência característica do concreto na idade do içamento (MPa). Valor típico: 15–25 MPa." |
| Fck,28 | "Resistência característica aos 28 dias (MPa). Usado para calcular ancoragem (NBR 6118 §9.3.2.2). Deve ser ≥ Fck,j." |
| Volume | "Volume da peça de concreto a ser içada, em metros cúbicos." |
| Cordoalha | "Tipo de cordoalha de protensão conforme NBR 7483." |
| Tipo de ancoragem | "Tipo de tratamento na extremidade da alça dentro do concreto. Dobra 90° e gancho 180° reduzem o comprimento necessário." |
| βa | "Coeficiente de amplificação dinâmica (NBR 9062). Padrão: 3,0. Simula efeitos dinâmicos do içamento." |
| γn | "Coeficiente de majoração (NBR 9062). Padrão: 1,30. Majoração total = βa × γn." |

---

## H. Sugestão de Layout Alternativo

```
┌──────────────────────────────────────────────────────────────────┐
│ Menu: Arquivo │ Ferramentas │ Ajuda                              │
├──────────────────────────────────────────────────────────────────┤
│ [Tab: Verificação]  [Tab: Memória de Cálculo]                    │
├─────────────────────┬────────────────────────────────────────────┤
│                     │                                            │
│  ┌─ Concreto ─────┐ │  ┌─ Resultado da Verificação ───────────┐ │
│  │ Fck,j    Fck,28│ │  │ ╔═══════════════════════════════════╗ │ │
│  └────────────────┘ │  │ ║  ✔ VERIFICAÇÃO APROVADA           ║ │ │
│  ┌─ Peça ─────────┐ │  │ ╚═══════════════════════════════════╝ │ │
│  │ Volume   Peso  │ │  │                                       │ │
│  └────────────────┘ │  │ ┌─ Indicadores (DESTAQUE) ──────────┐ │ │
│  ┌─ Cordoalha ────┐ │  │ │ FS: 2.34  [██████████░░] 234%     │ │ │
│  │ Tipo  Incl Alça│ │  │ │ Utiliz: 42.7% [████░░░░░░]        │ │ │
│  └────────────────┘ │  │ │ Mobiliz: 100% [██████████]         │ │ │
│  ┌─ Ancoragem ────┐ │  │ └───────────────────────────────────┘ │ │
│  │ Comp  Tipo Ader│ │  │                                       │ │
│  └────────────────┘ │  │ ▸ Cargas (colapsável)                 │ │
│  ┌─ Coeficientes ─┐ │  │ ▸ Propriedades dos materiais          │ │
│  │ βa       γn    │ │  │ ▸ Verificações                        │ │
│  └────────────────┘ │  └───────────────────────────────────────┘ │
│                     │                                            │
│  [Calcular Verif.]  │                                            │
│  [Restaurar Padrões]│                                            │
├─────────────────────┴────────────────────────────────────────────┤
│ ═══════ QSplitter (arrastável) ═══════                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─ Representação Gráfica ─────────────────────────────────────┐ │
│  │       ↑T                                                     │ │
│  │      ─○─         COTA: anc.nec = 51.2 cm                   │ │
│  │     / | \        COTA: anc.disp = 60.0 cm  ✔                │ │
│  │    /  |  \                                                   │ │
│  │  ╔════╧════╗     ← strand verde = OK                        │ │
│  │  ║CONCRETO ║        strand vermelho = insuficiente           │ │
│  │  ╚═════════╝                                                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────┤
│ StatusBar: ✔ Aprovado | FS = 2.34 | Utiliz. = 42.7%    v1.0.0  │
└──────────────────────────────────────────────────────────────────┘
```

**Mudanças-chave:**
1. QMenuBar no topo (Arquivo, Ferramentas, Ajuda)
2. Inputs agrupados em 5 sub-QGroupBox
3. Indicadores com barras visuais logo abaixo do banner
4. Seções secundárias colapsáveis
5. QSplitter entre dados/resultado e sketch
6. Sketch com cotas e cor condicional
7. QStatusBar com resumo + versão

---

## I. Checklist Final de Lançamento

- [ ] O usuário entende o que fazer em até 5 segundos?
- [ ] A ação principal (Calcular) está clara e acessível?
- [ ] Todos os campos têm labels descritivos com acentuação correta?
- [ ] Há feedback visual imediato após cada cálculo (banner + status bar)?
- [ ] Mensagens de reprovação explicam o que corrigir?
- [ ] A interface funciona inteiramente via teclado (Tab + Enter/F5)?
- [ ] Há contraste suficiente em todos os textos e controles?
- [ ] A interface funciona em resoluções diferentes (1366×768 até 4K)?
- [ ] Indicadores críticos (FS, utilização) são visíveis sem scroll?
- [ ] O visual é consistente (fontes, espaçamentos, cores, bordas)?
- [ ] Tooltips estão presentes em campos técnicos (βa, γn, tipo ancoragem)?
- [ ] A memória de cálculo pode ser copiada com um clique?

---

## J. Perguntas para Próxima Iteração

1. **Quantos engenheiros usam o app diariamente?** Isso define se vale investir em persistência (salvar/carregar) e preferências.

2. **Os coeficientes βa e γn são alterados com frequência ou quase sempre ficam no padrão?** Se ficam no padrão, podem ir para uma seção "Avançado" colapsável.

3. **O engenheiro costuma calcular várias peças em sequência?** Se sim, campo de identificação da peça e histórico de cálculos seriam muito valiosos.

4. **A memória de cálculo é colada em Word, Excel ou outro sistema?** Isso define o formato ideal de exportação (txt, HTML, PDF).

5. **Há necessidade de comparar cenários?** Ex.: "E se eu usar 3 alças em vez de 2?" — isso sugere implementar comparação lado a lado.

6. **Quais são os valores mais comuns de Fck,j na fábrica?** Presets como "15 MPa (desmoldagem)" e "25 MPa (protensão)" simplificariam o uso.

7. **O app será usado em tablets/telas touch na fábrica?** Isso impacta tamanho mínimo de botões e controles.

8. **Há outros tipos de alça além de cordoalha (barra, estribo)?** Determina se o modelo precisa ser extensível.

9. **O resultado precisa ser rastreável (log, carimbo de aprovação)?** Isso sugere cabeçalho com data/hora/responsável na memória.

10. **Qual a resolução de tela mais comum dos usuários?** Isso valida se o layout atual cabe sem scroll ou precisa de ajustes responsivos.
