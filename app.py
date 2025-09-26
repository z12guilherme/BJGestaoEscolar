from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, School, Student, Teacher, Turma, Nota
from functools import wraps
import os

# ---------------- Inicializar Flask ----------------
app = Flask(__name__)

# ---------------- Configurações ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://gestao_escolar_db_5jx5_user:Yi3VFMwLsxZIsN50RPLpy440Th7Rs80W@dpg-d3as2qjipnbc73fd56b0-a.oregon-postgres.render.com/gestao_escolar_db_5jx5'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"sslmode": "require"}}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-super-secreta')

# Inicializar banco de dados
db.init_app(app)

# ---------------- Criar tabelas e garantir root ----------------
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

def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            roles = required_roles if isinstance(required_roles, list) else [required_roles]
            # Root sempre tem acesso
            if not user or (user.role not in roles and user.role != 'Root'):
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
        if not user or user.role not in ['Professor', 'SecretarioEducacao', 'Root']:
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

@app.route('/turma/<int:turma_id>/manage')
@login_required
@professor_or_super_required
def manage_turma(turma_id):
    turma = Turma.query.get_or_404(turma_id)
    alunos = Student.query.filter_by(turma_id=turma.id).all()
    return render_template('turma_manage.html', turma=turma, alunos=alunos)

# ----------------- Rotas de Cadastro -----------------
@app.route('/school/register', methods=['GET', 'POST'])
@login_required
@role_required(['Root', 'SecretarioEducacao'])
def register_school():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        if not name or len(name) < 3:
            flash('Nome da escola é obrigatório e deve ter pelo menos 3 caracteres.', 'danger')
            return render_template('register_school.html')
        school = School(name=name, address=address)
        db.session.add(school)
        db.session.commit()
        flash('Escola cadastrada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register_school.html')

@app.route('/teacher/register', methods=['GET', 'POST'])
@login_required
@role_required(['Root', 'SecretarioEducacao'])
def register_teacher():
    schools = School.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        subject = request.form.get('subject')
        school_id = request.form.get('school_id')

        if not username or len(username) < 3:
            flash('Nome de usuário é obrigatório e deve ter pelo menos 3 caracteres.', 'danger')
            return render_template('register_teacher.html', schools=schools)
        if password != confirm_password or len(password) < 6:
            flash('As senhas devem coincidir e ter pelo menos 6 caracteres.', 'danger')
            return render_template('register_teacher.html', schools=schools)
        if not name or len(name) < 3:
            flash('Nome do professor é obrigatório e deve ter pelo menos 3 caracteres.', 'danger')
            return render_template('register_teacher.html', schools=schools)
        if not school_id:
            flash('Selecione uma escola.', 'danger')
            return render_template('register_teacher.html', schools=schools)

        teacher = Teacher(name=name, subject=subject, school_id=school_id)
        db.session.add(teacher)
        db.session.commit()

        user = User(username=username, role='Professor', school_id=school_id)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Professor cadastrado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register_teacher.html', schools=schools)

@app.route('/student/register', methods=['GET', 'POST'])
@login_required
@role_required(['Root', 'SecretarioEducacao'])
def register_student():
    schools = School.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        school_id = request.form.get('school_id')

        if not name or len(name) < 3:
            flash('Nome do aluno é obrigatório e deve ter pelo menos 3 caracteres.', 'danger')
            return render_template('register_student.html', schools=schools)
        if not school_id:
            flash('Selecione uma escola.', 'danger')
            return render_template('register_student.html', schools=schools)

        student = Student(name=name, birth_date=birth_date, school_id=school_id)
        db.session.add(student)
        db.session.commit()

        flash('Aluno cadastrado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register_student.html', schools=schools)

@app.route('/turma/register', methods=['GET', 'POST'])
@login_required
@role_required(['Root', 'SecretarioEducacao', 'Diretor'])
def register_turma():
    schools = School.query.all()
    teachers = Teacher.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        year = request.form.get('year')
        teacher_id = request.form.get('teacher_id')
        school_id = request.form.get('school_id')

        if not name or len(name) < 3:
            flash('Nome da turma é obrigatório e deve ter pelo menos 3 caracteres.', 'danger')
            return render_template('register_turma.html', schools=schools, teachers=teachers)
        if not school_id:
            flash('Selecione uma escola.', 'danger')
            return render_template('register_turma.html', schools=schools, teachers=teachers)

        turma = Turma(
            name=name,
            year=year if year else None,
            teacher_id=teacher_id if teacher_id else None,
            school_id=school_id
        )
        db.session.add(turma)
        db.session.commit()

        flash('Turma cadastrada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register_turma.html', schools=schools, teachers=teachers)

# ----------------- Exclusão de Turma -----------------
@app.route('/turma/<int:turma_id>/delete', methods=['POST'])
@login_required
@role_required(['Root', 'SecretarioEducacao', 'Diretor'])
def delete_turma(turma_id):
    turma = Turma.query.get_or_404(turma_id)
    db.session.delete(turma)
    db.session.commit()
    flash(f'Turma "{turma.name}" excluída com sucesso!', 'success')
    return redirect(url_for('dashboard'))

# ----------------- Rodar App -----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
