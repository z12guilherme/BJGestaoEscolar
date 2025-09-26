from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date

# Instância do SQLAlchemy (será inicializada no app.py)
db = SQLAlchemy()

class User(db.Model):
    """
    Modelo de usuário para o banco de dados.
    Armazena nome de usuário único e hash da senha.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'SecretarioEducacao', 'Diretor', 'Professor'
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Define o hash da senha usando Werkzeug."""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash."""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class School(db.Model):
    """
    Modelo de escola.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))

    teachers = db.relationship('Teacher', backref='school', lazy=True)
    turmas = db.relationship('Turma', backref='school', lazy=True)

    def __repr__(self):
        return f'<School {self.name}>'

class Student(db.Model):
    """
    Modelo de aluno.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(Date)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

class Teacher(db.Model):
    """
    Modelo de professor.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    turmas = db.relationship('Turma', backref='teacher', lazy=True)
    user = db.relationship('User', backref='teacher', uselist=False)

    def __repr__(self):
        return f'<Teacher {self.name}>'

class Turma(db.Model):
    """
    Modelo de turma.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)

    students = db.relationship('Student', backref='turma', lazy=True)
    notas = db.relationship('Nota', backref='turma', lazy=True)

    def __repr__(self):
        return f'<Turma {self.name}>'


class Nota(db.Model):
    """
    Modelo de nota.
    """
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    semestre = db.Column(db.String(20), nullable=False)  # Ex: "2025/1"
    valor = db.Column(db.Float, nullable=False)

    student = db.relationship('Student', backref='notas')

    def __repr__(self):
        return f'<Nota {self.valor} for Student {self.student_id}>'
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date

# Instância do SQLAlchemy (será inicializada no app.py)
db = SQLAlchemy()

class User(db.Model):
    """
    Modelo de usuário para o banco de dados.
    Armazena nome de usuário único e hash da senha.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # e.g., 'SecretarioEducacao', 'Diretor', 'Professor'
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Define o hash da senha usando Werkzeug."""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash."""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

class School(db.Model):
    """
    Modelo de escola.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))

    teachers = db.relationship('Teacher', backref='school', lazy=True)
    turmas = db.relationship('Turma', backref='school', lazy=True)

    def __repr__(self):
        return f'<School {self.name}>'

class Student(db.Model):
    """
    Modelo de aluno.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(Date)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

class Teacher(db.Model):
    """
    Modelo de professor.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    turmas = db.relationship('Turma', backref='teacher', lazy=True)
    user = db.relationship('User', backref='teacher', uselist=False)

    def __repr__(self):
        return f'<Teacher {self.name}>'

class Turma(db.Model):
    """
    Modelo de turma.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)

    students = db.relationship('Student', backref='turma', lazy=True)
    notas = db.relationship('Nota', backref='turma', lazy=True)

    def __repr__(self):
        return f'<Turma {self.name}>'


class Nota(db.Model):
    """
    Modelo de nota.
    """
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.id'), nullable=False)
    semestre = db.Column(db.String(20), nullable=False)  # Ex: "2025/1"
    valor = db.Column(db.Float, nullable=False)

    student = db.relationship('Student', backref='notas')

    def __repr__(self):
        return f'<Nota {self.valor} for Student {self.student_id}>'
