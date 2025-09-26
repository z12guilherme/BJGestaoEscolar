from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, School, Student, Teacher, Turma, Nota
from functools import wraps
import os

# Inicializar Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-super-segura')  # Em produção, use uma chave forte e variável de ambiente
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://gestao_escolar_db_5jx5_user:Yi3VFMwLsxZIsN50RPLpy440Th7Rs80W@dpg-d3as2qjipnbc73fd56b0-a.oregon-postgres.render.com/gestao_escolar_db_5jx5')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco de dados
db.init_app(app)

# Criar tabelas se não existirem
with app.app_context():
    db.create_all()

# Decorator para rotas protegidas
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
            if not user or user.role != required_role:
                flash('Acesso negado. Você não tem permissão para esta ação.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def professor_or_super_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or user.role not in ['Professor', 'SecretarioEducacao']:
            flash('Acesso negado. Apenas professores e superusuários podem acessar esta funcionalidade.', 'danger')
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

# Rota principal - redireciona para login se não logado, senão dashboard
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Rota de cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validação básica no backend
        if not username or not password:
            flash('Nome de usuário e senha são obrigatórios.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('register'))

        # Verificar se usuário já existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
            return redirect(url_for('register'))

        # Criar novo usuário
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Buscar usuário
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

# Rota do dashboard (protegida)
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

# Rota para cadastrar escola
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

        # Verificar se escola já existe
        existing_school = School.query.filter_by(name=name).first()
        if existing_school:
            flash('Escola já existe.', 'danger')
            return redirect(url_for('register_school'))

        # Criar nova escola
        new_school = School(name=name, address=address)
        db.session.add(new_school)
        db.session.commit()

        # Se for Diretor, associar a escola ao usuário
        if user.role == 'Diretor':
            user.school_id = new_school.id
            db.session.commit()

        flash('Escola cadastrada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register_school.html')

# Rota para cadastrar aluno
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

        # Para Diretor e Professor, school_id é fixo
        if user.role in ['Diretor', 'Professor']:
            school_id = user.school_id
        elif not school_id:
            flash('Escola é obrigatória.', 'danger')
            return redirect(url_for('register_student'))

        # Verificar se escola existe
        school = School.query.get(school_id)
        if not school:
            flash('Escola não encontrada.', 'danger')
            return redirect(url_for('register_student'))

        # Criar novo aluno
        new_student = Student(name=name, birth_date=birth_date, school_id=school_id)
        db.session.add(new_student)
        db.session.commit()

        flash('Aluno cadastrado com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    # Filtrar schools baseado no role
    if user.role in ['Diretor', 'Professor']:
        schools = [user.school] if user.school else []
    else:
        schools = School.query.all()
    return render_template('register_student.html', schools=schools)

# Rota para cadastrar professor (apenas para SecretarioEducacao)
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

        # Validação básica no backend
        if not username or not password or not name or not school_id:
            flash('Nome de usuário, senha, nome do professor e escola são obrigatórios.', 'danger')
            return redirect(url_for('register_teacher'))

        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('register_teacher'))

        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('register_teacher'))

        # Verificar se usuário já existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
            return redirect(url_for('register_teacher'))

        # Verificar se escola existe
        school = School.query.get(school_id)
        if not school:
            flash('Escola não encontrada.', 'danger')
            return redirect(url_for('register_teacher'))

        # Criar novo usuário
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Para obter o ID do usuário

        # Criar novo professor
        new_teacher = Teacher(name=name, subject=subject, school_id=school_id, user_id=new_user.id)
        db.session.add(new_teacher)
        db.session.commit()

        flash('Professor cadastrado com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    schools = School.query.all()
    return render_template('register_teacher.html', schools=schools)

# Rota para cadastrar turma
@app.route('/dashboard/register_turma', methods=['GET', 'POST'])
@login_required
def register_turma():
    user = get_current_user()
    if user.role not in ['SecretarioEducacao', 'Diretor', 'Professor']:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        year = request.form.get('year')
        teacher_id = request.form.get('teacher_id')
        school_id = request.form.get('school_id')

        if not name:
            flash('Nome é obrigatório.', 'danger')
            return redirect(url_for('register_turma'))

        # Para Professor, school_id é fixo e teacher_id é o próprio
        if user.role == 'Professor':
            teacher = get_current_teacher()
            if not teacher:
                flash('Erro: Professor não encontrado.', 'danger')
                return redirect(url_for('dashboard'))
            school_id = teacher.school_id
            teacher_id = teacher.id
        elif not school_id:
            flash('Escola é obrigatória.', 'danger')
            return redirect(url_for('register_turma'))

        # Verificar se escola existe
        school = School.query.get(school_id)
        if not school:
            flash('Escola não encontrada.', 'danger')
            return redirect(url_for('register_turma'))

        # Para Diretor, restringir à sua escola
        if user.role == 'Diretor' and user.school_id != int(school_id):
            flash('Você só pode cadastrar turmas na sua escola.', 'danger')
            return redirect(url_for('register_turma'))

        # Verificar se professor existe (opcional, mas para Professor é obrigatório)
        teacher = None
        if teacher_id:
            teacher = Teacher.query.get(teacher_id)
            if not teacher:
                flash('Professor não encontrado.', 'danger')
                return redirect(url_for('register_turma'))

        # Criar nova turma
        new_turma = Turma(name=name, year=year, teacher_id=teacher_id, school_id=school_id)
        db.session.add(new_turma)
        db.session.commit()

        flash('Turma cadastrada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    # Filtrar schools e teachers baseado no role
    if user.role == 'Professor':
        teacher = get_current_teacher()
        schools = [teacher.school] if teacher else []
        teachers = [teacher] if teacher else []
    elif user.role == 'Diretor':
        schools = [user.school] if user.school else []
        teachers = Teacher.query.filter_by(school_id=user.school_id).all() if user.school_id else []
    else:
        schools = School.query.all()
        teachers = Teacher.query.all()
    return render_template('register_turma.html', schools=schools, teachers=teachers)

# Rota para gerenciar turma (apenas para professores)
@app.route('/dashboard/turma/<int:turma_id>/manage', methods=['GET', 'POST'])
@login_required
def manage_turma(turma_id):
    teacher = get_current_teacher()
    if not teacher:
        flash('Acesso negado. Apenas professores podem gerenciar turmas.', 'danger')
        return redirect(url_for('dashboard'))

    turma = Turma.query.get_or_404(turma_id)
    if turma.teacher_id != teacher.id:
        flash('Você não tem permissão para gerenciar esta turma.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_student':
            name = request.form.get('name')
            birth_date = request.form.get('birth_date')
            if name:
                new_student = Student(name=name, birth_date=birth_date, school_id=turma.school_id, turma_id=turma_id)
                db.session.add(new_student)
                db.session.commit()
                flash('Aluno adicionado com sucesso!', 'success')
            else:
                flash('Nome do aluno é obrigatório.', 'danger')
        elif action == 'remove_student':
            student_id = request.form.get('student_id')
            student = Student.query.get_or_404(student_id)
            if student.turma_id == turma_id:
                db.session.delete(student)
                db.session.commit()
                flash('Aluno removido com sucesso!', 'success')
            else:
                flash('Erro ao remover aluno.', 'danger')

    students = Student.query.filter_by(turma_id=turma_id).all()
    return render_template('turma_manage.html', turma=turma, students=students)

# Rota para gerenciar usuários (apenas para SecretarioEducacao)
@app.route('/dashboard/manage_users', methods=['GET', 'POST'])
@role_required('SecretarioEducacao')
def manage_users():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        school_id = request.form.get('school_id')

        # Validação básica
        if not username or not password or not role:
            flash('Nome de usuário, senha e categoria são obrigatórios.', 'danger')
            return redirect(url_for('manage_users'))

        if password != confirm_password:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('manage_users'))

        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return redirect(url_for('manage_users'))

        # Verificar se usuário já existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
            return redirect(url_for('manage_users'))

        # Para Professor e Diretor, school_id é obrigatório
        if role in ['Professor', 'Diretor'] and not school_id:
            flash('Escola é obrigatória para Professores e Diretores.', 'danger')
            return redirect(url_for('manage_users'))

        # Verificar se escola existe se fornecida
        if school_id:
            school = School.query.get(school_id)
            if not school:
                flash('Escola não encontrada.', 'danger')
                return redirect(url_for('manage_users'))

        # Criar novo usuário
        new_user = User(username=username, role=role, school_id=school_id)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Para obter o ID

        # Se for Professor, criar Teacher
        if role == 'Professor':
            name = request.form.get('name')
            subject = request.form.get('subject')
            if not name:
                flash('Nome do professor é obrigatório.', 'danger')
                return redirect(url_for('manage_users'))
            new_teacher = Teacher(name=name, subject=subject, school_id=school_id, user_id=new_user.id)
            db.session.add(new_teacher)

        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('manage_users'))

    users = User.query.all()
    schools = School.query.all()
    return render_template('manage_users.html', users=users, schools=schools)


@app.route('/get_alunos/<int:turma_id>')
def get_alunos(turma_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Não autenticado'}), 401

    turma = Turma.query.get_or_404(turma_id)
    if user.role == 'SecretarioEducacao' or (user.role == 'Professor' and get_current_teacher().id == turma.teacher_id):
        students = Student.query.filter_by(turma_id=turma_id).all()
        return jsonify([{'id': s.id, 'name': s.name} for s in students])
    else:
        return jsonify({'error': 'Acesso negado'}), 403


@app.route('/dashboard/add_nota', methods=['GET', 'POST'])
@login_required
@professor_or_super_required
def add_nota():
    user = get_current_user()
    if request.method == 'GET':
        if user.role == 'Professor':
            teacher = get_current_teacher()
            turmas = Turma.query.filter_by(teacher_id=teacher.id).all()
        else:
            turmas = Turma.query.all()
        return render_template('add_nota.html', turmas=turmas)

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        turma_id = request.form.get('turma_id')
        semestre = request.form.get('semestre')
        valor = request.form.get('valor')

        if not all([student_id, turma_id, semestre, valor]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return redirect(url_for('add_nota'))

        turma = Turma.query.get(turma_id)
        if not turma:
            flash('Turma não encontrada.', 'danger')
            return redirect(url_for('add_nota'))

        if user.role == 'Professor' and get_current_teacher().id != turma.teacher_id:
            flash('Acesso negado à turma.', 'danger')
            return redirect(url_for('add_nota'))

        student = Student.query.get(student_id)
        if not student or student.turma_id != int(turma_id):
            flash('Aluno não pertence à turma selecionada.', 'danger')
            return redirect(url_for('add_nota'))

        try:
            valor = float(valor)
        except ValueError:
            flash('Valor da nota deve ser um número.', 'danger')
            return redirect(url_for('add_nota'))

        existing_nota = Nota.query.filter_by(student_id=student_id, turma_id=turma_id, semestre=semestre).first()
        if existing_nota:
            existing_nota.valor = valor
        else:
            new_nota = Nota(student_id=student_id, turma_id=turma_id, semestre=semestre, valor=valor)
            db.session.add(new_nota)

        db.session.commit()
        flash('Nota salva com sucesso!', 'success')
        return redirect(url_for('dashboard'))


@app.route('/dashboard/relatorios')
@login_required
@professor_or_super_required
def relatorios():
    user = get_current_user()
    if user.role == 'Professor':
        teacher = get_current_teacher()
        turmas = Turma.query.filter_by(teacher_id=teacher.id).all()
    else:
        turmas = Turma.query.all()

    notas_by_turma = {}
    for turma in turmas:
        notas_list = []
        notas = Nota.query.join(Student).filter(Nota.turma_id == turma.id).all()
        for nota in notas:
            notas_list.append({
                'student_name': nota.student.name,
                'semestre': nota.semestre,
                'valor': nota.valor
            })
        notas_by_turma[turma.id] = {'turma': turma, 'notas': notas_list}

    return render_template('relatorios.html', notas_by_turma=notas_by_turma)

# Rota de logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('login'))

# Executar app
if __name__ == '__main__':
    app.run(debug=True)
