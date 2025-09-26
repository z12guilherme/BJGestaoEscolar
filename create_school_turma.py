from app import app
from models import db, School, Turma, User

with app.app_context():
    # Checa se a escola já existe
    school = School.query.filter_by(name="Risoleta Cavalcante").first()
    if not school:
        school = School(name="Risoleta Cavalcante")
        db.session.add(school)
        db.session.commit()
        print("Escola 'Risoleta Cavalcante' criada com sucesso!")
    else:
        print("Escola 'Risoleta Cavalcante' já existe!")

    # Checa se a turma já existe
    turma = Turma.query.filter_by(name="Infantil 1").first()
    if not turma:
        turma = Turma(name="Infantil 1", school_id=school.id)
        db.session.add(turma)
        db.session.commit()
        print("Turma 'Infantil 1' criada com sucesso!")
    else:
        print("Turma 'Infantil 1' já existe!")

    # Opcional: associar root como responsável
    root_user = User.query.filter_by(username="root").first()
    if root_user and not root_user.school_id:
        root_user.school_id = school.id
        db.session.commit()
        print("Root associado à escola 'Risoleta Cavalcante'.")
