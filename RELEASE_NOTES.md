# Release Notes - GN_PRE_Icamento 1.0.0

## Status

Versao candidata para release tecnico 1.0.0.

As regras de negocio, interface principal, exportacoes e testes automatizados estao em estado estavel para validacao manual final em ambiente Windows limpo.

## Principais entregas

- Validacao robusta de entradas no core:
  - rejeicao de zero, negativos, `NaN` e infinitos;
  - validacao de `beta_a` e `gamma_n`;
  - validacao explicita de enums e tipo de cordoalha;
  - erros previsiveis via `ValidationError`.
- Testes de borda de calculo:
  - limites de inclinacao;
  - transicao de `fctm` em 50 MPa;
  - formula logaritmica para `fck > 50 MPa`;
  - casos governados por aco e por aderencia;
  - combinacoes de aprovacao/reprovacao de capacidade e ancoragem.
- Robustez da interface:
  - calculo automatico sempre que os dados de entrada mudam;
  - remocao do botao manual de calculo;
  - entrada invalida exibida como estado da tela, sem modal;
  - desenho tecnico protegido contra redimensionamento agressivo;
  - limite interno de 20 alcas no widget;
  - `QPainter` finalizado com seguranca;
  - atalhos mantidos em `self._shortcuts`.
- Exportacoes:
  - memoria de calculo em `.txt` com UTF-8;
  - desenho tecnico simplificado em `.svg`;
  - SVG gerado por `xml.etree.ElementTree`, com escaping automatico.
- Documentacao:
  - README alinhado as formulas reais;
  - escopo, entradas, saidas e exportacoes documentados;
  - versao alvo 1.0.0 registrada.
- Higiene de repositorio:
  - `.gitignore` criado para caches, temporarios, ambientes virtuais, builds e screenshots temporarios;
  - manifesto de limpeza Git registrado em `planofinal.md`.

## Validacao automatizada

- `python -B tools/release_check.py`
- `python -B -m unittest discover -s tests`
- 57 testes passando.
- Smoke tests offscreen da janela principal:
  - inicializacao;
  - ausencia de botao manual de calculo;
  - calculo aprovado;
  - calculo reprovado;
  - entrada invalida exibida automaticamente sem modal;
  - copia de memoria;
  - exportacao TXT mockada;
  - exportacao SVG mockada.
- `git diff --check` sem erros.
- Sem linhas Python acima de 99 caracteres em `app/` e `tests/`.
- Script de release em modo normal sem falhas; avisos restantes sao apenas `.pyc` e screenshots ja documentados.

## Pendencias antes do release final

Use `CHECKLIST_VALIDACAO_MANUAL.md` como roteiro oficial para fechar as validacoes manuais abaixo.

- Remover do controle de versao os `.pyc` ainda rastreados por Git.
- Decidir se os `screenshot_*.png` devem permanecer como evidencia visual ou sair do repositorio.
- Apagar manualmente os temporarios antigos bloqueados em `.tmp_test_outputs`, se ainda existirem.
- Rodar `python -B tools/release_check.py --strict` apos a limpeza dos artefatos rastreados.
- Executar em venv limpo no Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

- Validar manualmente:
  - caso aprovado;
  - caso reprovado;
  - copia da memoria;
  - exportacao TXT real;
  - exportacao SVG real;
  - gravacao real em caminho com acentos.
- Obter revisao final do engenheiro responsavel antes de uso operacional.
