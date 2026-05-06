# Verificador de Icamento com Cordoalhas (NBR 9062)

Aplicativo desktop para Windows, em Python 3.11+ e PySide6, para verificacao preliminar de icamento de pecas de concreto com alcas em cordoalha.

Versao alvo deste release: 1.0.0.

Os resultados sao recalculados automaticamente sempre que os dados de entrada sao alterados. Entradas invalidas aparecem como estado da propria tela, sem necessidade de botao manual de calculo.

## Escopo desta versao

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

## Exportacao

A versao atual exporta a memoria de calculo em arquivo `.txt` com codificacao UTF-8.

A versao atual tambem exporta um desenho tecnico simplificado em `.svg`, gerado por `app/infrastructure/svg_exporter.py`. O SVG inclui o croqui das alcas e um resumo dos principais resultados do calculo.

## Importante

Esta ferramenta e uma verificacao de engenharia preliminar. O dimensionamento final deve ser validado por engenheiro responsavel, com conferencia completa da NBR 9062, NBR 6118 e detalhes executivos do fabricante das alcas/dispositivos.

## Como executar (Windows)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

## Testes

```bash
python -m unittest discover -s tests
```
