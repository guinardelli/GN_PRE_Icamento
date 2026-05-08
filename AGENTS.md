# AGENTS.md

## Instruções para agentes de desenvolvimento

Este documento define as regras que devem ser seguidas por qualquer agente de IA, LLM ou ferramenta de desenvolvimento assistido ao trabalhar neste projeto.

O objetivo é criar e manter um aplicativo desktop para Windows usando **Python 3.11+** e **Tkinter/ttk**, com foco em simplicidade, estabilidade, clareza e facilidade de manutenção.

---

## 1. Prioridades do projeto

Ao tomar decisões técnicas, siga esta ordem de prioridade:

1. **Funcionalidade correta**
2. **Simplicidade**
3. **Clareza do código**
4. **Manutenibilidade**
5. **Boa separação de responsabilidades**
6. **Testabilidade**
7. **Extensibilidade apenas quando necessária**

Não sacrifique simplicidade para aplicar padrões arquiteturais desnecessários.

---

## 2. Stack obrigatória

- Linguagem: **Python 3.11+**
- Interface gráfica: **Tkinter/ttk**
- Sistema operacional alvo: **Windows**
- Ambiente virtual recomendado: `venv`
- Gerenciador de dependências: `pip`
- Empacotamento futuro, se necessário: `PyInstaller`

Evite adicionar dependências externas sem necessidade clara.

Antes de incluir uma nova biblioteca, verifique se ela:

- Reduz complexidade real
- Melhora estabilidade ou manutenção
- Evita reimplementação arriscada
- É compatível com Windows
- Não adiciona peso excessivo ao projeto

---

## 3. Princípios de desenvolvimento

### 3.1 Princípios gerais

Siga estes princípios durante todo o desenvolvimento:

- **DRY — Don’t Repeat Yourself**  
  Evite duplicação de código, regras, validações, constantes e lógica de negócio.

- **KISS — Keep It Simple**  
  Prefira soluções simples, explícitas e fáceis de entender.

- **YAGNI — You Aren’t Gonna Need It**  
  Não implemente funcionalidades, abstrações ou camadas que ainda não são necessárias.

- **Fail Fast**  
  Valide entradas e estados inválidos cedo, com mensagens claras.

- **Explicit is better than implicit**  
  Prefira código legível e direto em vez de soluções “inteligentes” demais.

### 3.2 SOLID de forma pragmática

Aplique SOLID sem exagero:

- **Single Responsibility Principle**  
  Cada classe, função ou módulo deve ter uma responsabilidade clara.

- **Open/Closed Principle**  
  Estruture o código para permitir extensão quando houver necessidade real.

- **Liskov Substitution Principle**  
  Subclasses devem poder substituir suas classes-base sem quebrar comportamento.

- **Interface Segregation Principle**  
  Prefira interfaces pequenas e específicas.

- **Dependency Inversion Principle**  
  Módulos de alto nível não devem depender diretamente de detalhes externos quando isso dificultar testes ou manutenção.

Não crie abstrações apenas para “parecer arquitetural”.

---

## 4. Escopo do aplicativo

O aplicativo deve ser:

- Desktop
- Voltado para Windows
- Simples de instalar e executar localmente
- Organizado em módulos pequenos
- Fácil de entender por outro desenvolvedor
- Estável diante de entradas inválidas
- Preparado para evolução gradual

Não implemente funcionalidades não solicitadas.

Quando houver dúvida, prefira uma primeira versão funcional simples.

---

## 5. Arquitetura recomendada

Use uma arquitetura simples em camadas.

Estrutura sugerida:

```text
app/
├── main.py
├── ui/
│   ├── main_window.py
│   ├── widgets/
│   └── styles.py
├── core/
│   ├── models.py
│   ├── services.py
│   └── exceptions.py
├── infrastructure/
│   ├── repositories.py
│   └── file_system.py
├── config/
│   └── settings.py
└── utils/
    └── helpers.py

tests/
├── test_services.py
└── test_models.py

requirements.txt
README.md
```

Essa estrutura é uma referência, não uma obrigação rígida.

Se o projeto for pequeno, simplifique.  
Não crie pastas, arquivos ou camadas vazias.

---

## 6. Responsabilidades por camada

### 6.1 `ui/`

Responsável por interface gráfica:

- Janelas
- Widgets
- Layouts
- Eventos de usuário
- Exibição de mensagens
- Conexão entre botões, campos e ações

A camada `ui/` não deve conter regras de negócio complexas.

Permitido:

- Validar campos simples antes de chamar serviços
- Exibir erros amigáveis
- Converter dados da interface para tipos esperados

Evite:

- Regras de negócio dentro de `QMainWindow`, dialogs ou widgets
- Acesso direto a arquivos ou banco de dados
- Lógica extensa em callbacks de botões

---

### 6.2 `core/`

Responsável pela lógica principal da aplicação:

- Modelos de domínio
- Serviços
- Validações principais
- Regras de negócio
- Exceções específicas do domínio

A camada `core/` deve ser a mais independente possível de Tkinter.

Sempre que possível, ela deve poder ser testada sem abrir a interface gráfica.

---

### 6.3 `infrastructure/`

Responsável por detalhes externos:

- Leitura e escrita de arquivos
- Persistência de dados
- Acesso ao sistema de arquivos
- Integrações futuras
- Implementações concretas de repositórios

Não coloque regras de negócio nesta camada.

---

### 6.4 `config/`

Responsável por configurações:

- Constantes globais
- Caminhos padrão
- Configurações de ambiente
- Metadados da aplicação

Evite espalhar constantes pelo código.

---

### 6.5 `utils/`

Responsável apenas por funções auxiliares genéricas e reutilizáveis.

Use com moderação.

Não transforme `utils/` em depósito de código sem responsabilidade clara.

Se uma função auxiliar pertence a uma regra de negócio, coloque-a em `core/`.

---

## 7. Diretrizes para Tkinter/ttk

### 7.1 Interface

A interface deve priorizar produtividade e clareza.

Requisitos:

- Usar tema claro
- Usar widgets nativos do Tkinter/ttk sempre que possível
- Manter visual limpo e consistente
- Usar fontes padrão do sistema
- Manter bom espaçamento entre elementos
- Evitar excesso de cores, sombras, bordas ou elementos decorativos

### 7.2 Usabilidade

A experiência do usuário deve ser objetiva.

Boas práticas:

- Botões com nomes claros e orientados à ação
- Campos com rótulos descritivos
- Mensagens de erro úteis e compreensíveis
- Fluxos principais acessíveis com poucos cliques
- Evitar janelas modais desnecessárias
- Não interromper o usuário sem motivo

### 7.3 Organização da interface

Prefira construir a interface em código Python claro e modular.

Evite arquivos `.ui` quando eles dificultarem a manutenção por agentes de IA.

Use callbacks, variáveis observáveis e eventos Tkinter de forma organizada.

Callbacks devem ser curtos.  
Se uma ação crescer demais, extraia a lógica para um método, serviço ou classe apropriada.

---

## 8. Padrões de código

### 8.1 Estilo

- Siga PEP 8
- Use nomes claros e descritivos
- Use type hints sempre que possível
- Organize imports
- Prefira funções pequenas
- Evite classes grandes demais
- Evite comentários óbvios
- Escreva docstrings em classes e funções importantes
- Use constantes nomeadas em vez de números mágicos

### 8.2 Nomes

Use nomes que expressem intenção.

Prefira:

```python
calculate_total_price()
load_user_settings()
FileRepository
SettingsService
```

Evite nomes genéricos sem contexto:

```python
Manager
Handler
Processor
Helper
do_stuff()
process_data()
```

Nomes genéricos só são aceitáveis quando o contexto for muito claro.

---

## 9. Tratamento de erros

Trate erros de forma específica e previsível.

Boas práticas:

- Capture exceções específicas
- Exiba mensagens amigáveis ao usuário
- Preserve detalhes técnicos para logs ou depuração
- Não silencie erros sem justificativa
- Não use `except Exception` indiscriminadamente

Exemplo preferível:

```python
try:
    data = repository.load(path)
except FileNotFoundError:
    raise AppError("Arquivo não encontrado.")
except PermissionError:
    raise AppError("Sem permissão para acessar o arquivo.")
```

Use exceções customizadas em `core/exceptions.py` quando isso melhorar a clareza.

---

## 10. Testes

Crie testes automatizados sempre que houver lógica de negócio relevante.

Priorize testes para:

- Serviços
- Modelos
- Validações
- Funções utilitárias importantes
- Regras de negócio

A interface gráfica não precisa ter testes complexos inicialmente.

Evite testar detalhes visuais frágeis.

O ideal é que a lógica principal possa ser testada sem instanciar janelas Tkinter.

---

## 11. Execução local

O projeto deve permitir execução local simples.

Comandos esperados no Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

O arquivo `requirements.txt` deve conter apenas dependências realmente usadas.

O projeto não deve ter dependências de runtime enquanto Tkinter/ttk for suficiente.

---

## 12. Empacotamento

Caso seja necessário gerar executável para Windows, use preferencialmente `PyInstaller`.

Comando base:

```bash
pyinstaller --noconfirm --onefile --windowed app/main.py
```

Não configure empacotamento avançado antes de a aplicação estar funcional.

Ajustes de ícone, versão, diretórios de saída e arquivos adicionais devem ser feitos apenas quando necessários.

---

## 13. Fluxo de trabalho para agentes

Ao receber uma tarefa, siga este fluxo:

1. Entenda o objetivo solicitado.
2. Identifique arquivos relevantes.
3. Faça a menor alteração suficiente para resolver o problema.
4. Preserve a estrutura existente sempre que ela estiver adequada.
5. Separe interface, regra de negócio e infraestrutura.
6. Atualize ou crie testes quando houver lógica testável.
7. Verifique se o projeto continua executável.
8. Revise o código antes de concluir.
9. Atualize o `README.md` se houver mudança em instalação, execução ou uso.

Não faça grandes refatorações sem necessidade.

Se uma refatoração for útil, ela deve ter motivo claro e escopo controlado.

---

## 14. Regras para alterações no código

Ao modificar o projeto:

- Não quebre APIs internas sem necessidade
- Não renomeie arquivos sem motivo claro
- Não mova código apenas por preferência estética
- Não adicione dependências sem justificativa
- Não implemente funcionalidades futuras não solicitadas
- Não misture mudanças de estilo com mudanças funcionais grandes
- Não introduza estado global desnecessário
- Não crie singletons sem necessidade real

Prefira alterações pequenas, coesas e fáceis de revisar.

---

## 15. Qualidade mínima antes de concluir

Antes de considerar uma tarefa concluída, verifique:

- O código executa sem erros óbvios
- A aplicação abre corretamente
- As principais ações funcionam
- Entradas inválidas não travam a aplicação
- A lógica de negócio está fora da interface
- Não há duplicação desnecessária
- Não foram criadas abstrações sem uso real
- Os nomes estão claros
- O código segue PEP 8
- Os testes relevantes foram criados ou atualizados
- O `requirements.txt` está coerente
- O `README.md` está atualizado quando necessário

---

## 16. Critérios de aceite do projeto

O projeto será considerado adequado quando:

- Rodar no Windows com Python 3.11+ e Tkinter/ttk
- Possuir interface clara, simples e em tema claro
- Ter estrutura modular e compreensível
- Separar interface, lógica de negócio e infraestrutura
- Seguir DRY, KISS, YAGNI e SOLID de forma pragmática
- Ter instruções claras de instalação e execução
- Ter testes para a lógica principal quando aplicável
- Ser fácil de evoluir sem grandes refatorações

---

## 17. O que evitar

Evite:

- Arquitetura complexa para um aplicativo simples
- Regras de negócio dentro da interface
- Classes abstratas sem uso real
- Bibliotecas pesadas sem justificativa
- Padrões de projeto aplicados por formalidade
- Arquivos gigantes com muitas responsabilidades
- Código excessivamente genérico
- Funções longas e difíceis de testar
- Nomes vagos como `Manager`, `Handler` ou `Processor`
- Funcionalidades não solicitadas
- Refatorações amplas sem necessidade
- Otimizações prematuras
- Comentários que apenas repetem o código

---

## 18. Orientação final

Faça primeiro uma versão funcional, simples e correta.

Depois melhore a estrutura com cuidado.

Mantenha o projeto fácil de entender, fácil de executar e fácil de evoluir.

A melhor solução é a que resolve o problema real com o menor nível de complexidade necessário.
