<<<<<<< HEAD
// Existing front-end validation and interactions (if any from previous implementation)
// For example, form validations for login/register, etc.
// ...

// Function for dynamic loading of students in add_nota form
function loadAlunos() {
    const turmaId = document.getElementById('turma_id').value;
    const alunoSelect = document.getElementById('student_id');
    if (!turmaId) {
        alunoSelect.innerHTML = '<option value="">Selecione um aluno</option>';
        alunoSelect.disabled = true;
        return;
    }

    fetch(`/get_alunos/${turmaId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Erro ao carregar alunos: ' + data.error);
                return;
            }
            alunoSelect.innerHTML = '<option value="">Selecione um aluno</option>';
            data.forEach(student => {
                const option = document.createElement('option');
                option.value = student.id;
                option.textContent = student.name;
                alunoSelect.appendChild(option);
            });
            alunoSelect.disabled = false;
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao carregar alunos.');
        });
}
=======
// Existing front-end validation and interactions (if any from previous implementation)
// For example, form validations for login/register, etc.
// ...

// Function for dynamic loading of students in add_nota form
function loadAlunos() {
    const turmaId = document.getElementById('turma_id').value;
    const alunoSelect = document.getElementById('student_id');
    if (!turmaId) {
        alunoSelect.innerHTML = '<option value="">Selecione um aluno</option>';
        alunoSelect.disabled = true;
        return;
    }

    fetch(`/get_alunos/${turmaId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Erro ao carregar alunos: ' + data.error);
                return;
            }
            alunoSelect.innerHTML = '<option value="">Selecione um aluno</option>';
            data.forEach(student => {
                const option = document.createElement('option');
                option.value = student.id;
                option.textContent = student.name;
                alunoSelect.appendChild(option);
            });
            alunoSelect.disabled = false;
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao carregar alunos.');
        });
}
>>>>>>> db5166d083e57d9cff6cad4f9277596e8fdc09f1
