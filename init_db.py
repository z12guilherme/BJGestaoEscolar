<<<<<<< HEAD
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

# Script opcional para inicializar o banco de dados
# Execute este script se precisar criar as tabelas manualmente: python init_db.py

with app.app_context():
    # Apaga todas as tabelas antigas
    db.drop_all()

    # Cria todas as tabelas de acordo com os modelos
    db.create_all()

    # Cria o superusuário root
    root = User(
        username='root',
        password_hash=generate_password_hash('Mg156810$'),
        role='SecretarioEducacao'
    )

    db.session.add(root)
    db.session.commit()

    print("Banco recriado e superusuário root criado com sucesso!")
=======
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

# Script opcional para inicializar o banco de dados
# Execute este script se precisar criar as tabelas manualmente: python init_db.py

with app.app_context():
    # Apaga todas as tabelas antigas
    db.drop_all()

    # Cria todas as tabelas de acordo com os modelos
    db.create_all()

    # Cria o superusuário root
    root = User(
        username='root',
        password_hash=generate_password_hash('Mg156810$'),
        role='SecretarioEducacao'
    )

    db.session.add(root)
    db.session.commit()

    print("Banco recriado e superusuário root criado com sucesso!")
>>>>>>> db5166d083e57d9cff6cad4f9277596e8fdc09f1
