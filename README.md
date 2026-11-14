# Gestão de Pedidos e Clientes

Sistema web desenvolvido com Flask e SQLAlchemy para auxiliar no gerenciamento de clientes, produtos e pedidos de um pequeno negócio de doces e salgados.

O projeto foi desenvolvido como parte do curso de Análise e Desenvolvimento de Sistemas, com o objetivo de facilitar a organização dos pedidos, o acompanhamento da produção e o controle das informações dos clientes.

**Aplicação publicada:** https://gestao-pedidos-clientes.onrender.com

## Objetivo

O sistema busca centralizar as informações que antes eram organizadas manualmente ou por meio de conversas no WhatsApp, oferecendo uma interface simples para cadastrar clientes, produtos, registrar pedidos, acompanhar seu andamento e consultar relatórios.

A solução foi planejada considerando a rotina de uma pequena empreendedora que trabalha individualmente, priorizando a facilidade de uso e a organização das atividades, sem depender de plataformas de entrega ou marketplaces.

## Funcionalidades

### Autenticação
- Login e logout de usuários.
- Cadastro de usuário administrador por meio de script.
- Armazenamento seguro de senhas utilizando hash.
- Proteção de páginas e rotas que exigem autenticação.

### Gerenciamento de clientes
- Cadastro de clientes.
- Listagem e consulta de clientes.
- Edição dos dados cadastrados.
- Exclusão de clientes.
- Visualização do histórico de pedidos de cada cliente.

### Gerenciamento de produtos
- Cadastro de produtos.
- Listagem e consulta de produtos.
- Edição dos dados cadastrados.
- Exclusão de produtos.
- Registro do nome e valor unitário dos produtos.

### Gerenciamento de pedidos
- Cadastro de pedidos associados a clientes.
- Inclusão de um ou mais itens em cada pedido.
- Seleção de produtos previamente cadastrados.
- Registro de quantidade e valor unitário dos itens.
- Definição da data e horário de retirada.
- Inclusão de observações.
- Edição e exclusão de pedidos.
- Atualização do status: pendente, em produção ou concluído.
- Consulta dos detalhes de cada pedido.

### Painel inicial
- Quantidade de pedidos pendentes.
- Quantidade de pedidos em produção.
- Quantidade de pedidos concluídos.
- Exibição das próximas retiradas.

### Relatórios
- Consulta de pedidos por período.
- Quantidade de pedidos no período selecionado.
- Valor total dos pedidos.
- Quantidade de pedidos por status.

### Outros recursos
- Interface web responsiva.
- Modo de alto contraste.
- Validação dos dados enviados pelos formulários.
- Proteção contra requisições não autorizadas.
- Proteção CSRF nos formulários.
- Endpoint `/health` para verificar a disponibilidade da aplicação e a conexão com o banco de dados.

## Tecnologias utilizadas

- Python: linguagem principal da aplicação.
- Flask: framework para desenvolvimento web.
- Flask-SQLAlchemy: integração e gerenciamento do banco de dados por meio de ORM.
- MySQL: sistema gerenciador de banco de dados utilizado no ambiente local.
- TiDB Cloud: banco de dados remoto utilizado na aplicação publicada.
- PyMySQL: driver de conexão entre Python e MySQL/TiDB.
- Flask-Login: gerenciamento de autenticação e sessões.
- Flask-WTF: proteção CSRF.
- HTML5: estrutura das páginas.
- CSS3: estilização e responsividade.
- JavaScript: funcionalidades de interação da interface.
- Jinja2: renderização dinâmica dos templates.
- Pytest: execução dos testes automatizados.
- python-dotenv: gerenciamento das variáveis de ambiente.
- Gunicorn: servidor WSGI utilizado na implantação.

## Estrutura do projeto

```text
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
│   ├── __init__.py
│   ├── criar_usuario.py
│   ├── criar_usuario_tidb.py
│   ├── criar_tabelas_tidb.py
│   └── testar_conexao_tidb.py
│
├── tests/
│   ├── conftest.py
│   └── testes automatizados[...]
│
├── config.py
├── requirements.txt
├── run.py
├── wsgi.py
├── .python-version
├── .gitignore
└── README.md
```

## Organização da aplicação

O projeto utiliza uma organização em camadas para separar as responsabilidades:

- Models: definem as entidades e os relacionamentos do banco de dados.
- Routes: definem os endpoints e recebem as requisições.
- Controllers: coordenam o processamento das requisições e as respostas.
- Services: concentram as regras de negócio e as operações com o banco de dados.
- Utils: armazenam funções auxiliares, validações e cálculos.
- Templates: contêm as páginas HTML renderizadas pelo Jinja2.
- Static: reúne os arquivos CSS e JavaScript.

## Banco de dados

O sistema utiliza SQLAlchemy para gerenciar as operações e os relacionamentos do banco de dados.

São utilizadas as seguintes tabelas:

| Tabela | Finalidade |
|---|---|
| usuarios | Armazena os usuários autorizados a acessar o sistema. |
| clientes | Armazena os dados dos clientes. |
| produtos | Armazena os produtos cadastrados e seus valores unitários. |
| pedidos | Armazena os pedidos, suas datas, status e observações. |
| itens_pedido | Armazena os itens associados a cada pedido, incluindo quantidade e valor unitário. |

No ambiente de desenvolvimento, é utilizado MySQL. Na aplicação publicada, o banco de dados está hospedado no TiDB Cloud.

Os relacionamentos entre as tabelas são gerenciados pelo SQLAlchemy.

## Como executar o projeto localmente

### 1. Pré-requisitos

- Python instalado.
- MySQL Server instalado e em execução.
- Git instalado.

### 2. Clonar o repositório

```bash
git clone https://github.com/bruno-has/gestao-pedidos-clientes.git

cd gestao-pedidos-clientes
```

### 3. Criar e ativar o ambiente virtual

No Windows, utilizando PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 5. Configurar o banco de dados

Crie o banco de dados no MySQL:

```sql
CREATE DATABASE gestao_pedidos_clientes
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

### 6. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua_chave_secreta
DATABASE_URL=mysql+pymysql://usuario:senha@localhost:3306/gestao_pedidos_clientes
FLASK_DEBUG=True
```

Substitua os valores de usuário e senha pelas credenciais do seu MySQL. Caso a senha contenha caracteres especiais, utilize a codificação URL correspondente.

**Importante:** o arquivo `.env` contém informações privadas e não deve ser enviado ao GitHub.

### 7. Criar as tabelas do banco de dados

Com o ambiente virtual ativado e o banco configurado, execute:

```bash
python -c "from app import create_app; from app.extensions import db; app = create_app(); ctx = app.app_context(); ctx.push(); db.create_all(); ctx.pop()"
```

### 8. Criar o usuário administrador

Execute o script:

```bash
python -m scripts.criar_usuario
```

Informe o nome, o e-mail e a senha solicitados no terminal.

### 9. Executar a aplicação

```bash
python run.py
```

A aplicação estará disponível em:

```text
http://127.0.0.1:5000
```

## API

Além da interface web, o projeto disponibiliza endpoints para operações de autenticação, clientes e pedidos.

| Recurso | Endpoint principal | Operações |
|---|---|---|
| Autenticação | `/auth` | Login, logout e consulta do usuário autenticado. |
| Clientes | `/clientes/` | Cadastro, listagem, consulta, atualização e exclusão. |
| Pedidos | `/pedidos/` | Cadastro, listagem, consulta, atualização e exclusão. |
| Pedidos por cliente | `/pedidos/cliente/<cliente_id>` | Consulta dos pedidos de um cliente. |
| Saúde da aplicação | `/health` | Verificação da aplicação e da conexão com o banco de dados. |

As rotas protegidas exigem autenticação. A proteção CSRF também está habilitada na aplicação.

## Testes automatizados

O projeto utiliza Pytest para verificar o funcionamento das funcionalidades e das regras de negócio.

Para executar todos os testes:

```bash
python -m pytest -v
```

Os testes utilizam uma configuração específica para execução, com banco de dados SQLite em memória, evitando alterações no banco de dados de desenvolvimento.

## Implantação

A aplicação está publicada na plataforma Render, utilizando um serviço Web para executar a aplicação Flask.

#### Endereço público:

https://gestao-pedidos-clientes.onrender.com

## Serviços utilizados

- Render: hospedagem da aplicação web.

- TiDB Cloud: banco de dados remoto.

- Gunicorn: servidor WSGI responsável por executar a aplicação em produção.

- GitHub: versionamento e armazenamento do código-fonte.

## Configuração de produção

A aplicação utiliza variáveis de ambiente configuradas diretamente no Render, incluindo a chave secreta e a URL de conexão com o banco de dados.

O arquivo wsgi.py disponibiliza a aplicação Flask para execução pelo Gunicorn.

Comando de inicialização utilizado:
```
gunicorn wsgi:app
```

## Verificação de disponibilidade

A aplicação disponibiliza o endpoint:
```
https://gestao-pedidos-clientes.onrender.com/health
```

Esse endpoint verifica a disponibilidade da aplicação e executa uma consulta ao banco de dados.

Em caso de sucesso, retorna:
```
{
  "status": "ok",
  "database": "connected"
}
```

A resposta HTTP 200 indica que a aplicação está disponível e conseguiu estabelecer conexão com o banco de dados.

Observação: o serviço gratuito do Render pode suspender a aplicação após um período de inatividade. Nesse caso, o primeiro acesso após a suspensão pode levar mais tempo devido à inicialização do serviço.

## Finalidade

Projeto acadêmico desenvolvido no curso de Análise e Desenvolvimento de Sistemas.