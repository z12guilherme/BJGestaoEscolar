from app import app  # importa seu Flask app
from models import db, User
from werkzeug.security import generate_password_hash

# Garante que tudo roda dentro do contexto do Flask
with app.app_context():
    # Cria tabelas se não existirem
    db.create_all()

    # Checa se o root já existe
    if not User.query.filter_by(username='root').first():
        root = User(
            username='root',
            password=generate_password_hash('Mg156810$')        )
        db.session.add(root)
        db.session.commit()
        print("Root criado com sucesso!")
    else:
        print("Root já existe!")
