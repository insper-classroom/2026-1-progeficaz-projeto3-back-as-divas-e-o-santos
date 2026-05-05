# Projeto 3 – Programação Eficaz (Backend)

Este repositório contém o **backend** do Projeto 3 da disciplina de Programação Eficaz.

## Sobre o projeto

O projeto consiste no desenvolvimento de um site para a lojinha do Insper, funcionando como um catálogo online de produtos.

Através da aplicação, o usuário pode:

* Visualizar os produtos disponíveis
* Consultar informações sobre os itens
* Realizar a reserva de produtos diretamente com a loja
* Atualizar informações de cadastro

---

## Tecnologias utilizadas

### Backend & Framework
* **Python** - Linguagem de programação principal
* **Flask** - Framework web para desenvolvimento da API REST
* **Flask-Session** - Gerenciamento de sessões no Flask

### Banco de Dados
* **MongoDB (Atlas)** - Banco de dados NoSQL em nuvem
* **PyMongo** - Driver Python para interação com MongoDB
* **BSON** - Formato de serialização de dados

### Processamento de Tarefas
* **Celery** - Sistema de fila de tarefas distribuído e assíncrono
* **Redis** - Message broker e backend para armazenamento de resultados do Celery
* **Billiard** - Processamento paralelo de tarefas
* **AMQP** - Protocolo de mensageria utilizado

### Testes
* **Pytest** - Framework de testes unitários
* **unittest.mock** - Mock e patch para testes

### APIs & Formatos
* **REST API** - Arquitetura de API
* **JSON** - Formato de serialização de dados

### Dependências Adicionais
* **Blinker** - Sistema de sinais para Flask
* **AMQPlib** - Biblioteca para protocolo AMQP

---

## Acesso ao projeto

O projeto completo (frontend + backend) está disponível online através de deploy na AWS.

Você pode acessá-lo pelo link abaixo:

🔗 <LINK_DO_PROJETO>

http://3.19.72.217
http://loja-insper-frontend.s3-website.us-east-2.amazonaws.com

## Equipe

* Marina Antuniassi
* Mariana Machado
* Maria Eduarda dos Santos
* Judite Mello
* Rafael Santos