# Sistema de Login Web

Este é um sistema web simples de cadastro e login de usuários, desenvolvido com Flask (Python) e SQLite. Inclui interface moderna e responsiva, validação de campos, armazenamento seguro de senhas e banco de dados local.

## Funcionalidades

- Cadastro de usuários com nome de usuário e senha.
- Login de usuários existentes.
- Interface responsiva com Bootstrap.
- Validação de campos no front-end (HTML5 e JavaScript).
- Feedback visual de sucesso e erro.
- Alternância entre telas de login e cadastro.
- Senhas armazenadas com hash seguro.
- Banco de dados SQLite criado automaticamente.

## Tecnologias Utilizadas

- **Backend**: Python 3, Flask, Flask-SQLAlchemy.
- **Banco de Dados**: SQLite.
- **Frontend**: HTML5, CSS3 (Bootstrap 5), JavaScript.
- **Segurança**: Hash de senhas com Werkzeug.

## Pré-requisitos

- Python 3.6 ou superior instalado.
- Pip (gerenciador de pacotes do Python).

## Instalação e Execução

1. **Clone ou baixe o projeto**:
   - Descompacte o projeto na pasta desejada.

2. **Instale as dependências**:
   - Abra o terminal na pasta do projeto (`sistema-login`).
   - Execute: `pip install -r requirements.txt`

3. **Execute o aplicativo**:
   - No terminal, execute: `python app.py`
   - O servidor será iniciado em `http://127.0.0.1:5000`.

4. **Acesse no navegador**:
   - Abra `http://127.0.0.1:5000` para acessar a página de login.
   - Use o link para alternar para cadastro.

## Estrutura do Projeto

```
sistema-login/
├── app.py                 # Aplicação principal Flask
├── models.py              # Modelo de dados (User)
├── init_db.py             # Script opcional para inicializar DB
├── requirements.txt       # Dependências Python
├── templates/             # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── static/                # Arquivos estáticos
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── instance/              # Pasta criada automaticamente para DB SQLite
    └── database.db
```

## Como Usar

- **Cadastro**: Acesse `/register`, preencha nome de usuário (único, alfanumérico) e senha (mín. 6 caracteres). Confirme a senha.
- **Login**: Acesse `/login`, insira credenciais válidas.
- **Dashboard**: Após login, acessa página protegida com opção de logout.
- **Validação**: Campos obrigatórios; senhas devem coincidir no cadastro.
- **Feedback**: Mensagens de sucesso (verde) ou erro (vermelho) aparecem após ações.

## Notas de Segurança

- Senhas são hashed com `generate_password_hash` (PBKDF2 por padrão).
- Sessões são gerenciadas pelo Flask (cookies seguros).
- Nome de usuário deve ser único; validação no backend.
- Para produção, considere HTTPS, rate limiting e validação mais robusta.

## Testes

- Teste cadastro com usuário novo.
- Teste login com credenciais corretas/incorretas.
- Teste alternância entre páginas.
- Verifique responsividade em dispositivos móveis.

## Contribuição

Sinta-se à vontade para melhorar o código ou adicionar funcionalidades (e.g., recuperação de senha).

## Licença

Este projeto é de código aberto. Use conforme necessário.
