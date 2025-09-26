from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, School, Student, Teacher, Turma, Nota
from functools import wraps
import os

# ==========================
# Configuração do Flask App
# ==========================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-super-segura')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://gestao_escolar_db_5jx5_user:Yi3VFMwLsxZIsN50RPLpy440Th7Rs80W@dpg-d3as2qjipnbc73fd56b0-a.oregon-postgres.render.com/gestao_escolar_db_5jx5'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco de dados
db.init_app(app)
with app.app_context():
    db.create_all()

# ==========================
# Funções Utilitárias
# ==========================
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

# ==========================
# Decorators de segurança
# ==========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    if not isinstance(required_role, list):
        required_role = [required_role]
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user or user.role not in required_role:
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

# ==========================
# Rotas
# ==========================
@app.route('/')
def index():
    return redirect(url_for('dashboard')) if 'user_id' in session else redirect(url_for('login'))

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
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('login'))

# ==========================
# Dashboard
# ==========================
@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    turmas = None
    schools = None
    if user.role == 'Professor':
        teacher = get_current_teacher()
        turmas = Turma.query.filter_by(teacher_id=teacher.id).all() if teacher else []
    elif user.role == 'Diretor':
        schools = [user.school] if user.school else []
        turmas = Turma.query.filter_by(school_id=user.school_id).all() if user.school_id else []
    elif user.role == 'SecretarioEducacao':
        schools = School.query.all()
        turmas = Turma.query.all()
    return render_template('dashboard.html', turmas=turmas, schools=schools)

# ==========================
# (Aqui você pode adicionar todas as outras rotas já existentes,
# como register_school, register_student, register_teacher, etc)
# mantendo a mesma lógica limpa e consistente.
# ==========================

# ==========================
# Executar app
# ==========================
if __name__ == '__main__':
    app.run(debug=True)
