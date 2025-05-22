
# Sistema de Impressão em Massa

Sistema para gerenciamento e impressão em lote de documentos.

## Requisitos

- Python 3.11 ou superior
- Windows: `pywin32` para impressão
- Linux: `cups` para impressão

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:

```bash
pip install flask requests python-dotenv
# Para Windows:
pip install pywin32
# Para Linux:
pip install pycups
```

3. Configure as variáveis de ambiente:
Crie um arquivo `.env` com:
```
API_TOKEN=seu_token_aqui
API_BASE_URL=url_da_api
```

## Executando

```bash
python main.py
```

O sistema estará disponível em `http://localhost:5000`

## Uso

1. Faça login usando seu token API
2. Selecione a impressora desejada
3. Escolha os documentos para impressão
4. Clique em "Imprimir Selecionados"
