# Verificador de Icamento com Cordoalhas (NBR 9062)

Aplicativo desktop para Windows, em Python 3.11+ e PySide6, para verificacao preliminar de icamento de pecas de concreto com alcas em cordoalha.

## Escopo desta versao

Entradas:

- Fck,j (MPa)
- Volume da peca (m3)
- Peso especifico do concreto (tf/m3)
- Tipo de cordoalha (CP 190-RB 9,5 / 12,7 / 15,2 mm)
- Inclinacao da cordoalha (graus)
- Ancoragem disponivel (cm)
- Condicao de aderencia (boa ou ma)
- Quantidade de alcas

Referencia visual:

- Painel "Secao e alca - Tipo A" na tela de entrada
- Se houver `image.png` na raiz do projeto ou em `app/image.png`, a imagem e exibida
- Sem arquivo, o app mostra um desenho padrao equivalente

Saidas:

- Massa da peca
- Massa majorada
- Ec,j
- fctm
- fptk
- fpyk
- fpyd
- fbpd
- Area da cordoalha
- Peso da cordoalha
- Ancoragem necessaria
- Carga maxima governante (aco x aderencia)
- Memoria de calculo com formulas e substituicao numerica

## Formulas adotadas

- `gk = volume * peso_especifico`
- `ged = gamma_f * beta_a * gk`, com `gamma_f = 1,3` e `beta_a = 3,0`
- `Ecj = 5600 * sqrt(fck,j)`
- `fctm = 0,3 * fck^(2/3)` (fck <= 50 MPa)
- `fctk,inf = 0,7 * fctm`
- `fctd = fctk,inf / gamma_c`, com `gamma_c = 1,3`
- `fpyk = 1710 MPa` e `fptk = 1900 MPa` para CP 190-RB
- `fpyd = fpyk / gamma_s`, com `gamma_s = 1,15`
- `fbpd = eta_p1 * eta_p2 * fctd`, com `eta_p1 = 1,2` (cordoalha 7 fios), `eta_p2 = 1,0` (boa) ou `0,7` (ma)
- Carga em cada alca: `T = ged / (n_alcas * sen(inclinacao))`
- Comprimento de ancoragem necessario:
  `Lnec = T / (fbpd * pi * diametro)`
- Areas e massas das cordoalhas CP 190-RB: valores nominais conforme ABNT NBR 7483:2021.

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
