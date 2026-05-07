# GN PRE - Calculadoras

Aplicativo desktop para Windows, em Python 3.11+ e PySide6, com calculadoras auxiliares para pre-fabricados.

A aplicacao abre em uma home compacta e sem menus. Cada calculadora abre em uma janela propria, acessada por botao/card, mantendo a navegacao clara e facilitando a inclusao gradual de novas ferramentas. Ao fechar a janela de uma calculadora, a home volta a ser exibida.

Calculadoras disponiveis nesta versao:

- Alca de icamento: verificacao preliminar de icamento de pecas de concreto com alcas em cordoalha.
- Comprimento de ancoragem: verificacao de ancoragem de barras passivas, emenda por transpasse e protensao aderente conforme NBR 6118.

Utilidades disponiveis nesta versao:

- Conversor bitola/espacamento: calcula espacamento equivalente entre armaduras considerando a classe de aco definida pela bitola selecionada.

Versao alvo deste release: 1.0.0.

Os resultados sao recalculados automaticamente sempre que os dados de entrada sao alterados. Entradas invalidas aparecem como estado da propria tela, sem necessidade de botao manual de calculo.

## Estrutura da aplicacao

- `app/main.py`: ponto de entrada.
- `app/ui/main_window.py`: home compacta e janelas das calculadoras.
- `app/ui/home_widget.py`: tela inicial com a lista de calculadoras disponiveis.
- `app/ui/calculators/`: widgets das calculadoras e registro simples.
- `app/core/`: modelos, validacoes e regras de negocio independentes da interface.
- `app/infrastructure/`: exportacoes e detalhes externos.

Para adicionar uma nova calculadora:

1. Criar um novo widget em `app/ui/calculators/`.
2. Manter regras de negocio testaveis em `app/core/`, quando houver logica relevante.
3. Registrar a calculadora em `app/ui/calculators/registry.py`.
4. Validar o fluxo Home -> Janela da calculadora -> fechar janela -> Home.

## Escopo da calculadora Alca de icamento

Entradas:

- Fck,j (MPa): resistencia do concreto na idade do icamento.
- Fck,28 (MPa): resistencia aos 28 dias, usada na verificacao de ancoragem.
- Volume da peca (m3).
- Peso especifico do concreto (tf/m3).
- Tipo de cordoalha CP 190-RB: 9,5 mm, 12,7 mm ou 15,2 mm.
- Inclinacao da cordoalha em relacao ao plano horizontal (graus).
- Ancoragem disponivel (cm).
- Tipo de ancoragem: reta, dobra 90 graus ou gancho 180 graus.
- Condicao de aderencia: boa ou ma.
- Quantidade de alcas.
- Coeficientes beta_a e gamma_n.

Saidas:

- Massa da peca.
- Massa majorada.
- Ec,j.
- fctm,j e fctm,28.
- fptk, fpyk e fpyd.
- fbpd,j para capacidade no icamento.
- fbpd,28 para comprimento de ancoragem.
- Area nominal e massa linear da cordoalha.
- Ancoragem necessaria.
- Carga maxima por aco, por aderencia e governante.
- Taxa de utilizacao e fator de seguranca.
- Memoria de calculo com formulas e substituicao numerica.

## Formulas adotadas

- `gk = volume * peso_especifico`
- `ged = gk * beta_a * gamma_n`
- `Ec,j = 0,9 * 5600 * sqrt(fck,j)`
- Para `fck <= 50 MPa`: `fctm = 0,3 * fck^(2/3)`
- Para `fck > 50 MPa`: `fctm = 2,12 * ln(1 + 0,11 * fck)`
- `fctk,inf = 0,7 * fctm`
- `fctd = fctk,inf / gamma_c`, com `gamma_c = 1,3`
- `fpyk = 1710 MPa` e `fptk = 1900 MPa` para CP 190-RB
- `fpyd = fpyk / gamma_s`, com `gamma_s = 1,15`
- `fbpd = eta_p1 * eta_p2 * fctd`
- `eta_p1 = 1,2` para cordoalha de 7 fios
- `eta_p2 = 1,0` para boa aderencia e `0,7` para ma aderencia
- Carga em cada alca: `T_alca = ged / (n_alcas * sen(inclinacao))`
- Carga em cada perna: `T_perna = T_alca / 2`
- Comprimento base de ancoragem:
  `Lnec,base = (T_perna * 9806,65) / (fbpd,28 * pi * diametro * 10)`
- Comprimento necessario:
  `Lnec = alpha * Lnec,base`

Coeficientes de ancoragem:

- Reta: `alpha = 1,00`
- Dobra 90 graus: `alpha = 0,70`
- Gancho 180 graus: `alpha = 0,50`

Areas e massas das cordoalhas CP 190-RB seguem valores nominais conforme ABNT NBR 7483:2021.

## Escopo da calculadora Comprimento de ancoragem

Referencia normativa principal: ABNT NBR 6118:2023 Versao Corrigida 2:2024.
Para categorias de aco e bitolas, a referencia de catalogo e a familia ABNT NBR 7480.

Entradas:

- Bitola comercial: 5,0; 6,3; 8,0; 10,0; 12,5; 16,0; 20,0; 25,0; 32,0 ou 40,0 mm.
- Fck (MPa).
- Tipo de aco: CA-25 lisa, CA-50 nervurada ou CA-60 entalhada.
- Condicao de aderencia: boa ou ma.
- Solicitacao: tracao ou compressao.
- Tipo de ancoragem: reta, com gancho, soldada ou com gancho e soldada.
- As,calc e As,ef (cm2).
- Comprimento disponivel (cm).

Saidas:

- fctm, fctk,inf, fctd, fyd e fbd.
- Comprimento basico `lb`.
- Comprimento minimo `lb,min`.
- Comprimento necessario `lb,nec`.
- As,ef necessaria quando `Ldisp < lb,nec` e `Ldisp >= lb,min`.
- Indicacao `N/A` para As,ef necessaria quando `Ldisp < lb,min`, pois aumentar a area nao atende ao minimo normativo.
- Croqui esquematico da ancoragem selecionada.

Coeficientes adotados para `lb,nec = max(alpha * lb * As,calc / As,ef, lb,min)`:

- Reta: `alpha = 1,00`.
- Com gancho: `alpha = 0,70`, somente para barras tracionadas.
- Soldada: `alpha = 0,70`, considerando barra transversal soldada.
- Com gancho e soldada: `alpha = 0,50`, somente para barras tracionadas.

Premissas e limitacoes:

- "Soldada" significa barra transversal soldada, nao chapa ou placa de ancoragem.
- Ganchos nao sao considerados para barras comprimidas.
- O croqui e esquematico e nao substitui desenho executivo.
- Feixes, telas soldadas, luvas, soldas e dispositivos mecanicos ficam fora desta versao.
- O dimensionamento final deve conferir cobrimentos, diametros de dobramento, solda, detalhamento e demais exigencias normativas aplicaveis.

### Aba Emenda por transpasse

A calculadora de comprimento de ancoragem possui uma aba principal para emendas por transpasse de barras passivas isoladas.

Entradas:

- Bitola comercial da barra 1 e da barra 2.
- Fck (MPa).
- Tipo de aco: CA-25, CA-50 ou CA-60.
- Condicao de aderencia: boa ou ma.
- Solicitacao: tracao ou compressao.
- Tipo de ancoragem base: reta, com gancho, soldada ou com gancho e soldada, respeitando a restricao de ganchos em compressao.
- As,calc e As,ef (cm2).
- Proporcao de barras emendadas na mesma secao.
- Distancia livre entre barras emendadas.
- Comprimento disponivel para transpasse.

Saidas:

- fctm, fctk,inf, fctd, fbd, lb e lb,nec.
- Coeficiente alpha0t para tracao, conforme faixa de barras emendadas.
- Comprimento de transpasse calculado, minimo normativo, acrescimo por distancia livre e comprimento final.
- Comparacao entre Ldisp e l0 final, com deficit quando nao atender.
- Avisos sobre bitola limite, armadura transversal, distancia livre maior que 4 phi e verificacao preliminar de espacamento.

Regras principais adotadas:

- Para tracao: `l0t = alpha0t * lb,nec`.
- Para tracao: `l0t,min = max(0,3 * alpha0t * lb; 15 phi; 20 cm)`.
- Para compressao: `l0c = lb,nec`.
- Para compressao: `l0c,min = max(0,6 * lb; 15 phi; 20 cm)`.
- Quando a distancia livre entre barras emendadas for maior que `4 phi`, essa distancia e acrescida ao comprimento em tracao.
- Emendas por transpasse sao bloqueadas para bitolas maiores que 32 mm.
- Quando as bitolas forem diferentes, a maior bitola e usada como referencia.
- A ferramenta alerta para armadura transversal quando `phi >= 16 mm` ou quando a proporcao de barras emendadas for `>= 25%`.

Limitacoes:

- Escopo limitado a barras isoladas.
- Feixes, luvas, soldas e dispositivos mecanicos devem ser dimensionados fora desta aba.
- O aviso de espacamento `>= max(2 phi; 20 mm)` e preliminar e deve ser confirmado no detalhamento conforme texto licenciado da NBR 6118.

### Aba Cordoalhas/Fios

A calculadora de comprimento de ancoragem tambem possui uma aba para protensao aderente.

Escopo:

- Fios conforme ABNT NBR 7482.
- Cordoalhas conforme ABNT NBR 7483.
- Verificacao auxiliar de comprimento necessario para desenvolver a tensao informada no aco.
- Memoria de calculo detalhada, com premissas, coeficientes, formulas simbolicas, substituicao numerica e unidades.

Entradas:

- Produto de protensao.
- Fck (MPa).
- Tensao considerada no aco (MPa).
- Comprimento disponivel (cm).
- Condicao de aderencia.

Saidas:

- fctm, fctk,inf e fctd.
- eta_p1, eta_p2 e fbpd.
- Forca considerada no aco.
- Comprimento necessario.
- Deficit, quando nao atender.

Limitacoes:

- A tensao no aco deve ser definida pelo engenheiro para a etapa de verificacao desejada.
- Nao substitui verificacoes de transferencia, perdas, fissuracao, comprimento de regularizacao, zonas de introducao de esforcos ou verificacao global da peca.
- Propriedades finais devem ser conferidas no texto licenciado das normas e nos certificados do lote.

## Importante

Esta ferramenta e uma verificacao de engenharia preliminar. O dimensionamento final deve ser validado por engenheiro responsavel, com conferencia completa da NBR 9062, NBR 6118 e detalhes executivos do fabricante das alcas/dispositivos.

## Como executar (Windows)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

## Como gerar o executavel Windows

O empacotamento usa PyInstaller em modo `onedir`, que e mais leve para iniciar e mais previsivel com PySide6 do que `onefile`.
O PyInstaller e dependencia apenas de build; nao precisa entrar no `requirements.txt` de execucao.

Se necessario, instale antes de empacotar:

```bash
pip install pyinstaller
```

```bash
powershell -ExecutionPolicy Bypass -File tools\build_exe.ps1
```

Saidas geradas:

- Pasta executavel: `dist\release_YYYYMMDD_HHMMSS\GN_PRE_Icamento\`
- Executavel: `GN_PRE_Icamento.exe`
- Pacote para distribuicao: `dist\GN_PRE_Icamento_1.0.0_windows.zip`

Para enviar a aplicacao a outro computador, use o `.zip` inteiro. O `.exe` depende das DLLs dentro da pasta `_internal`.

Tambem e possivel gerar um `.exe` unico, sem pasta auxiliar:

```bash
powershell -ExecutionPolicy Bypass -File tools\build_onefile_exe.ps1
```

Saida gerada:

- `dist\GN_PRE_Icamento_1.0.0_windows_onefile.exe`

Esse formato e mais simples de distribuir, mas pode demorar mais para abrir porque extrai as DLLs do PySide6 em uma pasta temporaria a cada execucao.
