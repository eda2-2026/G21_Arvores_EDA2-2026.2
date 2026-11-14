# Monitoramento de Temperatura de Estufa com Árvores AVL

## Alunos

| Matrícula | Aluno |
| --- | --- |
| 211041105 | Bruna de Lima Santos |
| 232014333 | Thiago Gomes Pereira de Abreu |

## Sobre

Projeto desenvolvido para a disciplina de Estruturas de Dados 2. O sistema
monitora temperaturas simuladas de uma estufa e utiliza duas árvores AVL
independentes, implementadas do zero em Python, para indexar as mesmas leituras
por critérios diferentes.

### Problema

Cada leitura contém um identificador, uma data/hora e uma temperatura. O sistema
precisa responder eficientemente a dois tipos de consulta:

- leituras realizadas dentro de um intervalo de datas e horários;
- leituras com temperatura estritamente acima de um limite.

Uma única árvore organizada por horário responderia bem à primeira consulta,
mas precisaria percorrer todas as leituras para consultar temperaturas. O mesmo
problema ocorreria no sentido inverso com uma árvore organizada apenas por
temperatura.

### Solução

O sistema mantém dois índices AVL sobre os mesmos objetos `Reading`:

| Índice | Chave de ordenação | Consulta principal |
| --- | --- | --- |
| Cronológico | `(timestamp, reading_id)` | Leituras entre dois instantes |
| Térmico | `(temperature, timestamp, reading_id)` | Leituras acima de um limite |

As chaves compostas permitem armazenar leituras com horários ou temperaturas
repetidos. O identificador é um inteiro positivo gerado pelo serviço de
monitoramento e diferencia completamente cada leitura.

Além das consultas, a aplicação permite inserção individual, importação de CSV,
geração de medições simuladas, percursos em ordem e exibição de métricas das
duas árvores.

### Algoritmo

Uma árvore AVL é uma árvore binária de busca autobalanceada. Para cada nó, o
fator de balanceamento é calculado por:

```text
altura da subárvore esquerda - altura da subárvore direita
```

Após cada inserção, esse valor deve permanecer entre `-1` e `1`. Quando a
invariante é violada, a árvore executa uma das seguintes correções:

- **LL:** rotação simples à direita;
- **RR:** rotação simples à esquerda;
- **LR:** rotação à esquerda no filho e depois à direita no nó;
- **RL:** rotação à direita no filho e depois à esquerda no nó.

A classe genérica `AVLTree` recebe uma função de chave, por isso a mesma
implementação atende aos índices cronológico e térmico. Os nós são imutáveis:
uma inserção reconstrói somente o caminho alterado e reutiliza os demais nós.

### Regras de indexação, consultas e métricas

#### Leituras e validação

- O formato de data/hora é `AAAA-MM-DD HH:MM:SS`.
- Datas e horários são locais, sem fuso horário.
- Temperaturas devem ser numéricas e finitas; `nan` e `inf` são rejeitados.
- Identificadores devem ser inteiros positivos.
- Leituras são imutáveis após sua criação.

#### Consultas

- A consulta cronológica inclui os dois extremos do intervalo.
- A consulta térmica retorna somente temperaturas estritamente maiores que o
  limite.
- Os resultados são devolvidos em ordem crescente da chave do índice.
- A busca por intervalo visita apenas as subárvores que podem conter resultados.

#### Consistência dos índices

O serviço prepara as atualizações em cópias rasas das duas árvores e publica os
novos índices somente depois que todas as inserções terminam. Se uma leitura ou
linha de CSV for inválida, nenhum dos índices é parcialmente atualizado e a
sequência de identificadores é preservada.

#### Convenções das métricas

| Métrica | Regra |
| --- | --- |
| Quantidade | Número de leituras e de nós em cada índice |
| Altura | Árvore vazia tem altura `0`; uma folha tem altura `1` |
| Rotações | Cada rotação simples conta uma unidade; uma rotação dupla conta duas |

As métricas são mantidas separadamente para os índices cronológico e térmico,
pois a ordem de inserção pode produzir estruturas e quantidades de rotações
diferentes.

### Complexidade

| Operação | Complexidade |
| --- | --- |
| Inserção em cada índice | `O(log n)` |
| Busca por chave completa | `O(log n)` |
| Consulta por intervalo ou temperatura | `O(log n + k)`, para `k` resultados |
| Percurso em ordem | `O(n)` |
| Armazenamento dos dois índices | `O(n)` por índice e `O(n)` assintótico total |

A altura de uma AVL permanece `O(log n)`. A inserção persistente aloca `O(log n)`
novos nós para reconstruir o caminho modificado; nós antigos sem referências
são liberados pelo Python.

### Código-base

O projeto foi desenvolvido do zero em Python e utiliza somente a biblioteca
padrão. A organização atual é:

```text
.
├── examples/
│   └── leituras.csv
├── models/
│   └── reading.py
├── services/
│   ├── importer.py
│   ├── monitor.py
│   └── simulator.py
├── tests/
│   ├── test_avl.py
│   ├── test_cli.py
│   ├── test_importer.py
│   ├── test_monitor.py
│   └── test_simulator.py
├── trees/
│   └── avl.py
├── main.py
└── README.md
```

- `models/reading.py`: modelo imutável, validações e funções de chave;
- `trees/avl.py`: AVL genérica, inserção, rotações, buscas e métricas;
- `services/monitor.py`: integração consistente dos dois índices;
- `services/importer.py`: leitura e validação de arquivos CSV;
- `services/simulator.py`: geração de medições simuladas;
- `main.py`: interface interativa de terminal;
- `tests/`: testes unitários e de integração.

## Screenshots

As capturas da execução no terminal serão adicionadas após a finalização da
demonstração.

### Menu principal

Captura pendente da tela com as opções da aplicação.

### Consultas pelos dois índices

Captura pendente das consultas por intervalo de horário e limite de temperatura.

### Estatísticas das árvores

Captura pendente das alturas e quantidades de rotações dos dois índices.

## Apresentação

O link para a apresentação será adicionado após a gravação.

## Instalação

### Pré-requisitos

Antes de começar, certifique-se de ter:

- Git;
- Python 3.10 ou superior.

Clone o repositório e acesse a pasta do projeto:

```bash
git clone https://github.com/eda2-2026/G21_Arvores_EDA2-2026.2.git
cd G21_Arvores_EDA2-2026.2
```

O projeto não possui dependências externas. Portanto, não é necessário instalar
pacotes adicionais nesta versão.

## Execução

Na raiz do projeto, execute:

```bash
python main.py
```

Em sistemas nos quais o comando padrão é `python3`, use:

```bash
python3 main.py
```

O menu oferece as seguintes opções:

| Opção | Operação |
| --- | --- |
| `1` | Inserir uma leitura individual |
| `2` | Importar leituras de um CSV |
| `3` | Consultar intervalo de datas e horários |
| `4` | Consultar temperaturas acima de um limite |
| `5` | Exibir quantidade, alturas e rotações |
| `6` | Listar leituras pelo índice cronológico |
| `7` | Listar leituras pelo índice térmico |
| `8` | Gerar e inserir leituras simuladas |
| `0` | Encerrar a aplicação |

### Importação de CSV

Selecione a opção `2` e informe o caminho do arquivo, por exemplo,
`examples/leituras.csv`. O arquivo deve usar UTF-8, com ou sem BOM, separação por
vírgulas e o seguinte cabeçalho:

```csv
data_hora,temperatura
2026-11-12 10:30:00,31.5
2026-11-12 10:30:00,31.5
2026-11-13 08:00:00,30.0
```

Campos ausentes ou extras, datas inválidas, temperaturas inválidas e erros de
formatação são rejeitados com indicação da linha. A importação é atômica: se
qualquer linha falhar, nenhuma leitura do arquivo é incorporada.

### Geração de leituras simuladas

Selecione a opção `8` e informe:

1. quantidade de leituras;
2. data/hora inicial;
3. intervalo em minutos;
4. temperatura mínima;
5. temperatura máxima.

As medições são geradas dentro da faixa informada e inseridas nos dois índices.
O serviço também aceita uma semente opcional quando utilizado diretamente pelo
código, permitindo reproduzir a mesma sequência em testes.

### Exemplo de demonstração

Importe `examples/leituras.csv` e consulte temperaturas acima de `30`. Depois,
consulte o intervalo de `2026-11-12 10:30:00` até o mesmo instante para mostrar
que leituras repetidas são preservadas. A opção `5` exibe as diferenças de
altura e rotações entre os dois índices.

## Testes

Para executar todos os testes, use na raiz do projeto:

```bash
python -m unittest discover -v
```

Se necessário, substitua `python` por `python3`.
