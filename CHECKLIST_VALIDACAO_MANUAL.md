# Checklist de Validacao Manual - GN_PRE_Icamento 1.0.0

Use este roteiro para fechar o release final em um ambiente Windows limpo.

## 1. Preparacao

- [ ] Confirmar Python 3.11 ou superior instalado.
- [ ] Abrir PowerShell na raiz do projeto.
- [ ] Criar ambiente virtual:

```bash
python -m venv .venv
```

- [ ] Ativar ambiente virtual:

```bash
.venv\Scripts\activate
```

- [ ] Instalar dependencias:

```bash
pip install -r requirements.txt
```

- [ ] Rodar testes:

```bash
python -m unittest discover -s tests
```

Resultado esperado:

- [ ] Todos os testes passam.

- [ ] Rodar checagem tecnica de release:

```bash
python -B tools\release_check.py
```

Resultado esperado:

- [ ] Sem falhas. Avisos sobre `.pyc` e screenshots sao aceitaveis apenas enquanto a limpeza Git nao estiver concluida.

## 2. Abertura da Aplicacao

- [ ] Executar:

```bash
python app/main.py
```

Resultado esperado:

- [ ] Janela abre sem erro.
- [ ] Titulo mostra `Verificador de Icamento - NBR 9062`.
- [ ] Dialogo "Sobre" mostra versao `1.0.0`.
- [ ] A tela inicial calcula automaticamente.
- [ ] Status inicial mostra verificacao aprovada ou reprovada de forma coerente com os valores padrao.
- [ ] Aba "Memoria de Calculo" contem texto gerado.

## 3. Caso Aprovado

Configurar:

- [ ] Volume: `0,05 m3`
- [ ] Numero de alcas: `4`
- [ ] Ancoragem disponivel: `300 cm`
- [ ] Manter demais valores padrao.

Resultado esperado:

- [ ] Status mostra `VERIFICACAO APROVADA`.
- [ ] Taxa de utilizacao menor ou igual a 100%.
- [ ] Fator de seguranca maior ou igual a 1,00.
- [ ] Desenho aparece em verde.
- [ ] Memoria mostra `RESULTADO FINAL: APROVADO`.

## 4. Caso Reprovado

Configurar:

- [ ] Volume: `100 m3`
- [ ] Numero de alcas: `1`
- [ ] Ancoragem disponivel: `1 cm`
- [ ] Manter demais valores padrao.

Resultado esperado:

- [ ] Status mostra `VERIFICACAO REPROVADA`.
- [ ] Taxa de utilizacao maior que 100% ou ancoragem insuficiente.
- [ ] Desenho aparece em vermelho.
- [ ] Campo de ancoragem fica destacado quando insuficiente.
- [ ] Memoria mostra `RESULTADO FINAL: REPROVADO`.

## 5. Validacao de Entrada Invalida

Configurar:

- [ ] Definir `Fck,j` maior que `Fck,28`.

Resultado esperado:

- [ ] Campo `Fck,28` fica destacado como invalido.
- [ ] Calculo nao trava a aplicacao.
- [ ] Status principal mostra `ENTRADA INVALIDA` automaticamente.
- [ ] Memoria informa que os dados devem ser corrigidos.

## 6. Copia da Memoria

- [ ] Ir para aba "Memoria de Calculo".
- [ ] Clicar em "Copiar Memoria".
- [ ] Colar em um editor de texto.

Resultado esperado:

- [ ] Texto colado contem `MEMORIA DE CALCULO`.
- [ ] Texto contem dados de entrada, formulas e resultado final.

## 7. Exportacao TXT Real

Usar um caminho com acentos, por exemplo:

```text
C:\Temp\Validação Içamento\memória_cálculo_ç.txt
```

Passos:

- [ ] Criar a pasta de destino.
- [ ] Menu Arquivo > Exportar Memoria (.txt).
- [ ] Salvar no caminho acima.

Resultado esperado:

- [ ] Arquivo `.txt` e criado.
- [ ] Arquivo abre corretamente em UTF-8.
- [ ] Conteudo contem `MEMORIA DE CALCULO`.
- [ ] Nao ha caracteres corrompidos em textos com acentos.

## 8. Exportacao SVG Real

Usar um caminho com acentos, por exemplo:

```text
C:\Temp\Validação Içamento\desenho_içamento_ç.svg
```

Passos:

- [ ] Menu Arquivo > Exportar Desenho (.svg).
- [ ] Salvar no caminho acima.
- [ ] Abrir o SVG no navegador ou visualizador compatível.

Resultado esperado:

- [ ] Arquivo `.svg` e criado.
- [ ] SVG abre sem erro.
- [ ] Desenho simplificado das alcas aparece.
- [ ] Resumo do calculo aparece no SVG.
- [ ] Status aprovado/reprovado aparece coerente com o calculo atual.

## 9. Limpeza Final do Repositorio

- [ ] Remover do controle de versao os `.pyc` listados em `planofinal.md`.
- [ ] Decidir se os `screenshot_*.png` permanecem no repositorio.
- [ ] Apagar `.tmp_test_outputs` se ainda existir e nao estiver bloqueado pelo OneDrive.
- [ ] Confirmar que `.gitignore` impede novos caches e temporarios.
- [ ] Rodar `python -B tools\release_check.py --strict` sem falhas apos a limpeza.

## 10. Aprovacao

- [ ] Engenheiro responsavel revisou premissas e resultados.
- [ ] Engenheiro responsavel aprovou uso operacional.
- [ ] Release pode ser marcado como final.
