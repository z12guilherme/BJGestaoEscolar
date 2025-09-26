from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, School, Student, Teacher, Turma, Nota
from functools import wraps
import os

# Inicializar Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-super-segura')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://gestao_escolar_db_5jx5_user:Yi3VFMwLsxZIsN50RPLpy440Th7Rs80W@dpg-d3as2qjipnbc73fd56b0-a.oregon-postgres.render.com/gestao_escolar_db_5jx5'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco de dados
db.init_app(app)

# Criar tabelas e garantir root
with app.app_context():
    db.create_all()
    root_user = User.query.filter_by(username="root").first()
    if not root_user:
        root_user = User(username="root", role="Root")
        root_user.set_password("Mg156810$")
        db.session.add(root_user)
        db.session.commit()
        print("Usuário root criado com sucesso!")
    else:
        if root_user.role != "Root":
            root_user.role = "Root"
            db.session.commit()
            print("Usuário root atualizado para role Root.")

# ----------------- Decorators -----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user or user.role not in (required_role if isinstance(required_role, list) else [required_role]):
                flash('Acesso negado. Você não tem permissão para esta ação.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def root_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != 'Root':
            flash('Acesso negado. Apenas o Root pode acessar esta ação.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def professor_or_super_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or user.role not in ['Professor', 'SecretarioEducacao']:
            flash('Acesso negado. Apenas professores e superusuários podem acessar esta funcionalidade.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------- Helpers -----------------
def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def get_current_teacher():
    user = get_current_user()
    if user and user.role == 'Professor' and user.teacher:
        return user.teacher
    return None

# ----------------- Rotas principais -----------------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['school_id'] = user.school_id
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        flash('Credenciais inválidas. Tente novamente.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    turmas = None
    schools = None
    if user.role == 'Professor':
        teacher = get_current_teacher()
        if teacher:
            turmas = Turma.query.filter_by(teacher_id=teacher.id).all()
    elif user.role == 'Diretor':
        if user.school_id:
            schools = [user.school]
            turmas = Turma.query.filter_by(school_id=user.school_id).all()
    elif user.role in ['SecretarioEducacao', 'Root']:
        schools = School.query.all()
        turmas = Turma.query.all()
    return render_template('dashboard.html', turmas=turmas, schools=schools)

# ----------------- Todas as outras rotas mantidas -----------------
# ... aqui você mantém todas as rotas de gerenciamento de usuários, cadastro de escolas, alunos, professores, turmas, etc.

# ----------------- Rodar App -----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
