# Monitoramento de temperatura de estufa — Grupo 21

Projeto de Estrutura de Dados II: monitoramento com leituras simuladas e duas
árvores AVL implementadas do zero em Python. Uma única classe genérica mantém
dois índices independentes sobre os mesmos objetos `Reading`:

| Índice | Chave | Consulta |
| --- | --- | --- |
| Cronológico | `(timestamp, reading_id)` | Leituras entre duas datas/horários |
| Térmico | `(temperature, timestamp, reading_id)` | Temperaturas acima de um limite |

Os IDs são inteiros positivos gerados pelo serviço. Leituras com horário e
temperatura idênticos recebem IDs diferentes e são preservadas.

## Executar

Requer Python 3.10 ou superior. O projeto usa apenas a biblioteca padrão,
sem dependências externas. Na raiz do repositório:

```sh
python main.py
```

O menu permite inserir leituras, importar CSV, consultar os dois índices,
mostrar o total de leituras e as alturas, e listar os percursos em ordem.
Use `AAAA-MM-DD HH:MM:SS` para datas e ponto como separador decimal.
Datas e horários são locais, sem fuso horário.

As consultas por horário incluem os dois extremos. A consulta por temperatura
retorna somente leituras **estritamente acima** do limite, em ordem crescente
de temperatura, horário e ID. Dados ficam em memória durante a execução;
nenhum arquivo é modificado pela importação.

## Importar CSV

Selecione a opção `2` e informe o caminho do arquivo, por exemplo,
`examples/leituras.csv`. O formato é UTF-8 (com ou sem BOM), separado por
vírgulas, com o cabeçalho abaixo na mesma ordem:

```csv
data_hora,temperatura
2026-11-12 10:30:00,31.5
2026-11-12 10:30:00,31.5
2026-11-13 08:00:00,30.0
```

Cada linha usa a mesma rotina de inserção individual. Datas inválidas,
temperaturas não finitas (`nan`, `inf`) e linhas com campos faltantes ou extras
são rejeitadas. Erros nas linhas indicam o número da linha. Se houver erro,
**nenhuma leitura do arquivo é incorporada**, e os dados anteriores e a
sequência de IDs são preservados. Um arquivo contendo apenas o cabeçalho
importa zero leituras.

Para uma demonstração, importe o arquivo de exemplo e consulte temperaturas
acima de `30`: serão retornadas três leituras. Consulte também o intervalo
`2026-11-12 10:30:00` até `2026-11-12 10:30:00`: as duas leituras repetidas
desse horário serão preservadas.

## Estrutura e funcionamento

- `models/reading.py`: leitura imutável, validação e funções de chave.
- `trees/avl.py`: inserção, rotações LL/RR/LR/RL, busca, intervalo e percurso.
- `services/monitor.py`: IDs, inserção consistente nos dois índices e consultas.
- `services/importer.py`: leitura e validação de CSV.
- `main.py`: interface de terminal.
- `tests/`: testes das estruturas, serviço, CSV e menu.

A altura da árvore vazia é `0`; uma folha tem altura `1`. O fator de
balanceamento é a altura à esquerda menos a altura à direita, entre `-1` e `1`
após cada inserção. Chaves completas duplicadas na AVL genérica causam erro.

Os nós da AVL são imutáveis. Uma inserção reconstrói apenas os nós do caminho
alterado e aplica as rotações necessárias. O serviço prepara as duas árvores
em cópias rasas e só as publica quando todas as inserções terminam. Isso evita
atualizar apenas um índice em caso de falha, sem copiar a árvore inteira.
Essa garantia vale para a aplicação de terminal, de execução sequencial.

| Operação | Complexidade |
| --- | --- |
| Inserção por índice / busca exata | `O(log n)` |
| Consulta por intervalo / temperatura | `O(log n + k)`, para `k` resultados |
| Percurso em ordem | `O(n)` |
| Armazenamento dos dois índices | `O(n)` |

Uma inserção aloca `O(log n)` nós ao reconstruir o caminho; os nós antigos sem
referências são liberados pelo Python. Uma importação também mantém as novas
leituras em memória até confirmar o lote completo.

## Testes

```sh
python -m unittest discover -v
```

Os testes verificam os quatro casos de rotação, as invariantes em todos os nós,
inserções crescentes, decrescentes e aleatórias, consultas com poda de subárvores,
leituras repetidas, limites inclusivos, temperaturas estritamente acima do
limite, consistência após falhas, CSV com 100 e 1.000 registros e o fluxo do menu.

Sensores reais, banco de dados, interface gráfica, remoção, gerador automático
de CSV e contador de rotações não fazem parte desta implementação.
