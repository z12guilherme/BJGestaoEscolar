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
        root_user.set_password("Mg156810$")  # senha do root
        db.session.add(root_user)
        db.session.commit()
        print("Usuário root criado com sucesso!")
    else:
        if root_user.role != "Root":
            root_user.role = "Root"
            db.session.commit()
            print("Usuário root atualizado para role Root.")

# Decorators
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
            user_id = session.get('user_id')
            if not user_id:
                flash('Você precisa fazer login para acessar esta página.', 'danger')
                return redirect(url_for('login'))
            user = User.query.get(user_id)
            if not user or user.role not in (required_role if isinstance(required_role, list) else [required_role]):
                flash('Acesso negado. Você não tem permissão para esta ação.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def root_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Você precisa fazer login para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        user = User.query.get(user_id)
        if not user or user.role != 'Root':
            flash('Acesso negado. Apenas o Root pode acessar esta ação.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

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

# Rotas principais
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
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

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
    elif user.role == 'SecretarioEducacao':
        schools = School.query.all()
        turmas = Turma.query.all()
    return render_template('dashboard.html', turmas=turmas, schools=schools)

# ----------------- GERENCIAR USUÁRIOS -----------------
@app.route('/dashboard/manage_users', methods=['GET', 'POST'])
@role_required('SecretarioEducacao')
def manage_users():
    schools = School.query.all()
    users = User.query.all()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        name = request.form.get('name')
        subject = request.form.get('subject')
        school_id = request.form.get('school_id')

        if not username or not password or not role:
            flash('Nome de usuário, senha e categoria são obrigatórios.', 'danger')
            return redirect(url_for('manage_users'))
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('manage_users'))
        if len(password) < 6:
            flash('Senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('manage_users'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nome de usuário já existe.', 'danger')
            return redirect(url_for('manage_users'))

        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # Se for professor, criar também o registro Teacher
        if role == 'Professor':
            if not name or not subject or not school_id:
                flash('Para professor, nome, matéria e escola são obrigatórios.', 'danger')
                return redirect(url_for('manage_users'))
            new_teacher = Teacher(name=name, subject=subject, school_id=school_id, user_id=new_user.id)
            db.session.add(new_teacher)

        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('manage_users.html', users=users, schools=schools)

@app.route('/dashboard/edit_user/<int:user_id>', methods=['GET', 'POST'])
@role_required('SecretarioEducacao')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role')
        if username:
            user.username = username
        if role:
            user.role = role
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('manage_users'))
    return render_template('edit_user.html', user=user)

@app.route('/dashboard/delete_user/<int:user_id>', methods=['POST'])
@role_required('SecretarioEducacao')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'Root':
        flash('Não é possível deletar o usuário Root.', 'danger')
        return redirect(url_for('manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('Usuário deletado com sucesso!', 'success')
    return redirect(url_for('manage_users'))

# ----------------- ROTAS DE CADASTRO -----------------
@app.route('/dashboard/register_school', methods=['GET', 'POST'])
@login_required
def register_school():
    user = get_current_user()
    if user.role not in ['SecretarioEducacao', 'Diretor']:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        if not name:
            flash('Nome da escola é obrigatório.', 'danger')
            return redirect(url_for('register_school'))
        existing_school = School.query.filter_by(name=name).first()
        if existing_school:
            flash('Escola já existe.', 'danger')
            return redirect(url_for('register_school'))
        new_school = School(name=name, address=address)
        db.session.add(new_school)
        db.session.commit()
        if user.role == 'Diretor':
            user.school_id = new_school.id
            db.session.commit()
        flash('Escola cadastrada com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register_school.html')

@app.route('/dashboard/register_student', methods=['GET', 'POST'])
@login_required
def register_student():
    user = get_current_user()
    if user.role not in ['SecretarioEducacao', 'Diretor', 'Professor']:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        school_id = request.form.get('school_id')
        if not name:
            flash('Nome é obrigatório.', 'danger')
            return redirect(url_for('register_student'))
        if user.role in ['Diretor', 'Professor']:
            school_id = user.school_id
        elif not school_id:
            flash('Escola é obrigatória.', 'danger')
            return redirect(url_for('register_student'))
        school = School.query.get(school_id)
        if not school:
            flash('Escola não encontrada.', 'danger')
            return redirect(url_for('register_student'))
        new_student = Student(name=name, birth_date=birth_date, school_id=school_id)
        db.session.add(new_student)
        db.session.commit()
        flash('Aluno cadastrado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    if user.role in ['Diretor', 'Professor']:
        schools = [user.school] if user.school else []
    else:
        schools = School.query.all()
    return render_template('register_student.html', schools=schools)

@app.route('/dashboard/register_teacher', methods=['GET', 'POST'])
@role_required('SecretarioEducacao')
def register_teacher():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        subject = request.form.get('subject')
        school_id = request.form.get('school_id')
        if not username or not password or not name or not school_id:
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('register_teacher'))
        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('register_teacher'))
        if len(password) < 6:
            flash('Senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('register_teacher'))
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nome de usuário já existe.', 'danger')
            return redirect(url_for('register_teacher'))
        school = School.query.get(school_id)
        if not school:
            flash('Escola não encontrada.', 'danger')
            return redirect(url_for('register_teacher'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()
        new_teacher = Teacher(name=name, subject=subject, school_id=school_id, user_id=new_user.id)
        db.session.add(new_teacher)
        db.session.commit()
        flash('Professor cadastrado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    schools = School.query.all()
    return render_template('register_teacher.html', schools=schools)

# ----------------- LOGOUT -----------------
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

# Executar app
if __name__ == '__main__':
    app.run(debug=True)
