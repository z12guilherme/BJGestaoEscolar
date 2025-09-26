from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, School, Student, Teacher, Turma, Nota
from functools import wraps
import os

# Inicializar Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-super-segura')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://usuario:senha@host:porta/banco')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
        print("Usuário root criado!")
    elif root_user.role != "Root":
        root_user.role = "Root"
        db.session.commit()
        print("Usuário root atualizado para role Root.")

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Faça login para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            # Root tem acesso a tudo
            if user and user.role == 'Root':
                return f(*args, **kwargs)
            if not user or user.role not in (roles if isinstance(roles, list) else [roles]):
                flash('Acesso negado.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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

# Rotas
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
        flash('Credenciais inválidas.', 'danger')
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
    elif user.role in ['SecretarioEducacao', 'Root']:
        schools = School.query.all()
        turmas = Turma.query.all()
    return render_template('dashboard.html', turmas=turmas, schools=schools)

# Gerenciamento de usuários (Root e Superuser)
@app.route('/dashboard/manage_users', methods=['GET', 'POST'])
@role_required(['Root', 'SecretarioEducacao'])
def manage_users():
    users = User.query.all()
    schools = School.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        school_id = request.form.get('school_id') or None
        name = request.form.get('name')
        subject = request.form.get('subject')
        
        if not username or not password or password != confirm_password or not role:
            flash('Preencha todos os campos corretamente.', 'danger')
            return redirect(url_for('manage_users'))
        
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe.', 'danger')
            return redirect(url_for('manage_users'))
        
        new_user = User(username=username, role=role, school_id=school_id)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()
        
        if role == 'Professor' and name and subject:
            teacher = Teacher(name=name, subject=subject, school_id=school_id, user_id=new_user.id)
            db.session.add(teacher)
        
        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('manage_users.html', users=users, schools=schools)

@app.route('/dashboard/edit_user/<int:user_id>', methods=['GET', 'POST'])
@role_required(['Root', 'SecretarioEducacao'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form.get('username') or user.username
        user.role = request.form.get('role') or user.role
        db.session.commit()
        flash('Usuário atualizado!', 'success')
        return redirect(url_for('manage_users'))
    return render_template('edit_user.html', user=user)

@app.route('/dashboard/delete_user/<int:user_id>', methods=['POST'])
@role_required(['Root', 'SecretarioEducacao'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'Root':
        flash('Não é permitido deletar o Root!', 'danger')
        return redirect(url_for('manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('Usuário deletado!', 'success')
    return redirect(url_for('manage_users'))

# Logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
