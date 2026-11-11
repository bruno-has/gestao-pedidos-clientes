# Gestão de Pedidos e Clientes

Sistema web desenvolvido com Flask e MySQL para auxiliar no gerenciamento de clientes e pedidos de um pequeno negócio de doces e salgados.

O projeto foi desenvolvido como parte do curso de Análise e Desenvolvimento de Sistemas, com o objetivo de facilitar a organização dos pedidos, o acompanhamento da produção e o controle das informações dos clientes.

## Objetivo

O sistema busca centralizar as informações que antes eram organizadas manualmente ou por meio de conversas no WhatsApp, oferecendo uma interface simples para cadastrar clientes, registrar pedidos, acompanhar seu andamento e consultar relatórios.

A solução foi planejada considerando a rotina de uma pequena empreendedora que trabalha individualmente, priorizando a facilidade de uso e a organização das atividades, sem depender de plataformas de entrega ou marketplaces.

## Funcionalidades

### Autenticação
- Login e logout de usuários
- Cadastro de usuário administrador por meio de script
- Armazenamento seguro de senhas utilizando hash
- Proteção de páginas e rotas que exigem autenticação

### Gerenciamento de clientes
- Cadastro de clientes
- Listagem e consulta de clientes
- Edição dos dados cadastrados
- Exclusão de clientes
- Visualização do histórico de pedidos de cada cliente

### Gerenciamento de pedidos
- Cadastro de pedido associados a clientes
- Inclusão de um ou mais itens em cada pedido
- Registro de quantidade e valor unitário dos itens
- Definição da data e horário de retirada
- Inclusão de observações
- Edição e exclusão de pedidos
- Atualização do status: pendente, em produção ou concluído
- Consulta dos detalhes de cada pedido

### Painel inicial
- Quantidade de pedidos pendentes
- Quantidade de pedidos em produção
- Quantidade de pedidos concluídos
- Exibição das próximas retiradas

### Relatórios
- Consulta de pedidos por período
- Quantidade de pedidos no período selecionado
- Valor total dos pedidos
- Quantidade de pedidos por status

### Outros recursos
- Interface web responsiva
- Validação dos dados enviados pelos formulários
- Proteção contra requisições não autorizadas
- Proteção CSRF nos formulários
- Endpoint de verificação da disponibilidade da aplicação e da conexão com o banco de dados (/health)

## Tecnologias utilizadas

- Python: linguagem principal da aplicação
- Flask: framework para desenvolvimento web
- Flask-SQLAlchemy: integração e gerenciamento do banco de dados por meio de ORM
- MySQL: sistema de gerenciador de banco de dados
- PyMySQL: driver de conexão entre Python e MySQL
- Flask-Login: gerenciamento de autenticação e sessões
- Flask-WTF: proteção CSRF
- HTML5: estrutura das páginas
- CSS3: estilização e responsividade
- JavaScript: funcionalidades de interação da interface
- Jinja2: renderização dinâmica dos templates
- Pytest: execução dos testes automatizados
- python-dotenv: gerenciamento das variáveis de ambiente

## Estrutura do projeto
```
gestao-pedidos-clientes/
│
├── app/
│   ├── controllers/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── utils/
│   ├── __init__.py
│   └── extensions.py
│
├── scripts/
│   └── criar_usuario.py
│
├── tests/
│   ├── conftest.py
│   └── testes automatizados
│
├── config.py
├── requirements.txt
├── run.py
├── .env
├── .gitignore
└── README.md
```



## Organização da aplicação

O projeto utiliza uma organização em camadas para separar as responsabilidades:

- Models: definem as entidades e os relacionamentos do banco de dados
- Routes: definem os endpoints e recebem as requisições
- Controllers: coordenam o processamento das requisições e as respostas
- Services: concentram as regras de negócio e as operações com o banco de dados
- Utils: armazenam funções auxiliares, validações e cálculos
- Templates: contêm as páginas HTML renderizadas pelo Jinja2
- Static: reúne os arquivos CSS e JavaScript

## Banco de dados

O sistema utiliza MySQL e possui as seguintes tabelas:

| Tabela | Finalidade | 
|--------|------------|
|usuarios| Armazena os usuários autorizados a acessar o sistema
|clientes| Armazena os dados dos clientes
|pedidos | Armazena os pedidos, suas datas, status e observações
|itens_pedido| Armazena os itens associados a cada pedido, incluindo quantidade e valor unitário

Os relacionamentos entre as tabelas são gerenciados pelo SQLAlchemy.

## Como executar o projeto

1. Pré-requisitos
* Python instalado
* MySQL Server instalado e em execução
* Git instalado

&nbsp;

2. Clonar o repositório
```
git clone https://github.com/bruno-has/gestao-pedidos-clientes.git

cd gestao-pedidos-clientes
```

&nbsp;

3. Criar e ativar o ambiente virtual

No Windows, utilizando PowerShell:
```
py -m venv venv
.\venv\Scripts\Activate.ps1
```

&nbsp;

4. Instalar as dependências
```
python -m pip install -r requirements.txt
```

&nbsp;

5. Configurar o banco de dados

Crie o banco de dados no MySQL:
```
CREATE DATABASE gestao_pedidos_clientes
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

&nbsp;

6. Configurar as variáveis de ambiente

Crie um arquivo .env na raiz do projeto:
```
SECRET_KEY=sua_chave_secreta
DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/gestao_pedidos_clientes
FLASK_DEBUG=True
```

Substitua os valores de usuário e senha pelas credenciais do seu MySQL. Caso a senha contenha caracteres especiais, utilize a codificação URL correspondente.

Importante: o arquivo .env contém informações privadas e não deve ser enviado ao GitHub.

&nbsp;

7. Criar as tabelas do banco de dados

Com o ambiente virtual ativado e o banco configurado, execute:
```
python -c "from app import create_app; from app.extensions import db; app = create_app(); ctx = app.app_context(); ctx.push(); db.create_all(); ctx.pop()"
```

&nbsp;

8. Criar o usuário administrador

Execute o script:
```
python -m scripts.criar_usuario
```

Informe o nome, o e-mail e a senha solicitados no terminal.

&nbsp;

9. Executar a aplicação
```
python run.py
```

A aplicação estará disponível em:
```
http://127.0.0.1:5000
```

---

## API

Além da interface web, o projeto disponibiliza endpoints REST para operações de autenticação, clientes e pedidos.

|Recurso|Endpoint principal|Operações
|-------|------------------|---------
|Autenticação | /auth | Login, logout e consulta do usuário autenticado
|Clientes | /clientes/ | Cadastro, listagem, consulta, atualização e exclusão
|Pedidos | /pedidos/ | Cadastro, listagem, consulta, atualização e exclusão
|Pedidos por cliente | /pedidos/cliente/<cliente_id> | Consulta dos pedidos de um cliente
|Saúde da aplicação | /health | Verificação da aplicação e da conexão com o banco de dados

&nbsp;

As rotas protegidas exigem autenticação. A proteção CSRF também está habilitada na aplicação.

## Testes automatizados

O projeto utiliza Pytest para verificar o funcionamento das funcionalidades e das regras de negócio.

Para executar todos os testes:
```
python -m pytest -v
```
Os testes utilizam uma configuração específica para execução, com banco de dados SQLite em memória, evitando alterações no banco de dados de desenvolvimento.

## Finalidade

Projeto acadêmico do curso de Análise e Desenvolvimento de Sistemas.