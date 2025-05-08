
# Iacá Backend

Este repositório contém o backend da aplicação Iacá, um sistema de compra e venda de caroço de açaí desenvolvido em FastAPI.

## Como Rodar o Projeto

### 1. Clone o repositório
```bash
git clone https://github.com/ThiagoRosa21/Iaca-Backend.git
cd Iaca-Backend/Backend_iaca
````

### 2. Instale as dependências

```bash
pip install -r app/requirements.txt
```

### 3. Rode o servidor

```bash
python -m uvicorn app.main:app --reload
```

Acesse a API em [http://localhost:8000](http://localhost:8000)

## Documentação Interativa

* Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
* Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Tecnologias

* FastAPI
* SQLite + SQLAlchemy
* Autenticação JWT
* Pydantic
* Uvicorn


