from flask import Flask, render_template_string, request, jsonify, session
from functools import wraps
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Admin credentials
ADMIN_CREDENTIALS = {
    'admin': 'admin123'
}

# In-memory storage
EXAMS = {
    'python_basics': {
        'title': 'Python Basics',
        'duration': 30,
        'questions': [
            {
                'id': 1,
                'question': 'What is the output of print(type([]))?',
                'options': ['<class \'list\'>', '<class \'tuple\'>', '<class \'dict\'>', '<class \'set\'>'],
                'correct': 0
            },
            {
                'id': 2,
                'question': 'Which keyword is used to create a function in Python?',
                'options': ['function', 'def', 'func', 'define'],
                'correct': 1
            }
        ]
    }
}

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Online Examination System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .role-selector {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 40px;
        }

        .role-card {
            background: white;
            border-radius: 15px;
            padding: 40px;
            width: 300px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .role-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }

        .role-card .icon {
            font-size: 4em;
            margin-bottom: 20px;
        }

        .role-card h2 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }

        .hidden {
            display: none;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }

        .form-group input, .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
        }

        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
            margin-right: 10px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
            background: #6c757d;
            color: white;
        }

        .btn-danger {
            background: #dc3545;
            color: white;
        }

        .exam-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .exam-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 25px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .exam-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        }

        .exam-card h3 {
            font-size: 1.5em;
            margin-bottom: 15px;
        }

        .exam-info {
            display: flex;
            justify-content: space-between;
            font-size: 0.9em;
            margin-top: 10px;
        }

        .question-container {
            margin-top: 20px;
        }

        .question-text {
            font-size: 1.3em;
            margin-bottom: 25px;
            color: #333;
            line-height: 1.6;
        }

        .options {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .option {
            padding: 18px 25px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #f9f9f9;
        }

        .option:hover {
            border-color: #667eea;
            background: #f0f0ff;
            transform: translateX(5px);
        }

        .option.selected {
            border-color: #667eea;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
        }

        .timer {
            font-size: 1.5em;
            font-weight: bold;
            color: #764ba2;
            padding: 10px 20px;
            background: #f5f5f5;
            border-radius: 8px;
            display: inline-block;
            margin-bottom: 20px;
        }

        .timer.warning {
            color: #e74c3c;
            animation: pulse 1s infinite;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 10px;
            margin-bottom: 20px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }

        .result-container {
            text-align: center;
        }

        .score {
            font-size: 4em;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 30px 0;
        }

        .result-details {
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
            flex-wrap: wrap;
            gap: 20px;
        }

        .result-item {
            padding: 20px;
            background: #f9f9f9;
            border-radius: 10px;
            flex: 1;
            min-width: 150px;
        }

        .result-item h4 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .result-item p {
            font-size: 1.5em;
            font-weight: bold;
        }

        .admin-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #e0e0e0;
        }

        .tab {
            padding: 15px 30px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 1.1em;
            font-weight: bold;
            color: #666;
            transition: all 0.3s ease;
        }

        .tab.active {
            color: #667eea;
            border-bottom: 3px solid #667eea;
        }

        .question-item {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }

        .question-item h4 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .option-input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            align-items: center;
        }

        .option-input-group input[type="radio"] {
            width: auto;
        }

        .option-input-group input[type="text"] {
            flex: 1;
        }

        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .admin-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Online Examination System</h1>
            <p>Advanced exam platform with admin controls</p>
        </div>

        <!-- Role Selection -->
        <div class="role-selector" id="roleSelector">
            <div class="role-card" onclick="selectRole('admin')">
                <div class="icon">👨‍💼</div>
                <h2>Admin</h2>
                <p>Manage exams and questions</p>
            </div>
            <div class="role-card" onclick="selectRole('student')">
                <div class="icon">👨‍🎓</div>
                <h2>Student</h2>
                <p>Take exams and test your knowledge</p>
            </div>
        </div>

        <!-- Admin Login -->
        <div class="card hidden" id="adminLogin">
            <button class="btn btn-secondary" onclick="backToRole()">← Back</button>
            <h2 style="margin: 20px 0; color: #667eea;">Admin Login</h2>
            <div id="loginAlert"></div>
            <div class="form-group">
                <label>Username</label>
                <input type="text" id="adminUsername" placeholder="Enter username">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" id="adminPassword" placeholder="Enter password">
            </div>
            <button class="btn btn-primary" onclick="adminLogin()">Login</button>
            <p style="margin-top: 15px; color: #666;">Default: admin / admin123</p>
        </div>

        <!-- Admin Panel -->
        <div class="card hidden" id="adminPanel">
            <div class="admin-header">
                <h2 style="color: #667eea;">Admin Dashboard</h2>
                <button class="btn btn-danger" onclick="adminLogout()">Logout</button>
            </div>

            <div class="admin-tabs">
                <button class="tab active" onclick="switchTab('manage')">Manage Exams</button>
                <button class="tab" onclick="switchTab('add')">Add New Exam</button>
            </div>

            <div id="manageTab">
                <h3 style="margin-bottom: 20px; color: #667eea;">Existing Exams</h3>
                <div id="adminExamList"></div>
            </div>

            <div id="addTab" class="hidden">
                <h3 style="margin-bottom: 20px; color: #667eea;">Create New Exam</h3>
                <div id="examAlert"></div>
                <div class="form-group">
                    <label>Exam Title</label>
                    <input type="text" id="examTitle" placeholder="e.g., JavaScript Basics">
                </div>
                <div class="form-group">
                    <label>Duration (minutes)</label>
                    <input type="number" id="examDuration" placeholder="30" min="1">
                </div>
                <div class="form-group">
                    <label>Questions</label>
                    <div id="questionsContainer"></div>
                    <button class="btn btn-secondary" onclick="addQuestion()" style="margin-top: 10px;">+ Add Question</button>
                </div>
                <button class="btn btn-primary" onclick="createExam()">Create Exam</button>
            </div>
        </div>

        <!-- Student Section -->
        <div class="card hidden" id="studentInfo">
            <button class="btn btn-secondary" onclick="backToRole()">← Back</button>
            <h2 style="margin: 20px 0; color: #667eea;">Student Information</h2>
            <div class="form-group">
                <label>Full Name *</label>
                <input type="text" id="studentName" placeholder="Enter your name">
            </div>
            <div class="form-group">
                <label>Email *</label>
                <input type="email" id="studentEmail" placeholder="Enter your email">
            </div>
            <div class="form-group">
                <label>Student ID *</label>
                <input type="text" id="studentId" placeholder="Enter your ID">
            </div>
        </div>

        <div class="card hidden" id="examSelection">
            <h2 style="margin-bottom: 20px; color: #667eea;">Select an Exam</h2>
            <div class="exam-list" id="examList"></div>
        </div>

        <div class="card hidden" id="examContainer">
            <div class="progress-bar">
                <div class="progress-fill" id="progressBar"></div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div id="questionNumber" style="font-weight: bold; font-size: 1.2em; color: #667eea;"></div>
                <div class="timer" id="timer">00:00</div>
            </div>
            <div class="question-text" id="questionText"></div>
            <div class="options" id="options"></div>
            <div style="margin-top: 30px; display: flex; justify-content: space-between;">
                <button class="btn btn-secondary" id="prevBtn" onclick="prevQuestion()">Previous</button>
                <button class="btn btn-primary" id="nextBtn" onclick="nextQuestion()">Next</button>
                <button class="btn btn-primary hidden" id="submitBtn" onclick="submitExam()">Submit Exam</button>
            </div>
        </div>

        <div class="card hidden" id="resultContainer">
            <div class="result-container">
                <h2 style="color: #667eea; margin-bottom: 20px;">Exam Results</h2>
                <div class="score" id="score"></div>
                <div class="result-details">
                    <div class="result-item">
                        <h4>Total Questions</h4>
                        <p id="totalQuestions"></p>
                    </div>
                    <div class="result-item">
                        <h4>Correct Answers</h4>
                        <p id="correctAnswers"></p>
                    </div>
                    <div class="result-item">
                        <h4>Wrong Answers</h4>
                        <p id="wrongAnswers"></p>
                    </div>
                    <div class="result-item">
                        <h4>Time Taken</h4>
                        <p id="timeTaken"></p>
                    </div>
                </div>
                <button class="btn btn-primary" onclick="restartExam()">Take Another Exam</button>
            </div>
        </div>
    </div>

    <script>
        let questionCounter = 0;
        let currentExam = null;
        let currentQuestion = 0;
        let answers = {};
        let timeLeft = 0;
        let timerInterval = null;
        let startTime = null;
        let studentInfo = {};

        function hideAll() {
            document.querySelectorAll('.card').forEach(el => el.classList.add('hidden'));
            document.getElementById('roleSelector').classList.add('hidden');
        }

        function selectRole(role) {
            hideAll();
            if (role === 'admin') {
                document.getElementById('adminLogin').classList.remove('hidden');
            } else {
                document.getElementById('studentInfo').classList.remove('hidden');
                document.getElementById('examSelection').classList.remove('hidden');
                loadExams();
            }
        }

        function backToRole() {
            location.reload();
        }

        async function adminLogin() {
            const username = document.getElementById('adminUsername').value;
            const password = document.getElementById('adminPassword').value;

            const res = await fetch('/api/admin/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });

            const data = await res.json();
            
            if (data.success) {
                hideAll();
                document.getElementById('adminPanel').classList.remove('hidden');
                loadAdminExams();
            } else {
                document.getElementById('loginAlert').innerHTML = 
                    '<div class="alert alert-error">Invalid credentials</div>';
            }
        }

        function adminLogout() {
            fetch('/api/admin/logout', {method: 'POST'}).then(() => location.reload());
        }

        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            if (tab === 'manage') {
                document.querySelector('.tab:nth-child(1)').classList.add('active');
                document.getElementById('manageTab').classList.remove('hidden');
                document.getElementById('addTab').classList.add('hidden');
                loadAdminExams();
            } else {
                document.querySelector('.tab:nth-child(2)').classList.add('active');
                document.getElementById('manageTab').classList.add('hidden');
                document.getElementById('addTab').classList.remove('hidden');
            }
        }

        function addQuestion() {
            questionCounter++;
            const div = document.createElement('div');
            div.className = 'question-item';
            div.id = 'q' + questionCounter;
            div.innerHTML = `
                <h4>Question ${questionCounter}</h4>
                <div class="form-group">
                    <label>Question Text</label>
                    <textarea rows="3" id="qtext${questionCounter}"></textarea>
                </div>
                <div class="form-group">
                    <label>Options (select correct answer)</label>
                    ${[0,1,2,3].map(i => `
                        <div class="option-input-group">
                            <input type="radio" name="qcorrect${questionCounter}" value="${i}">
                            <input type="text" id="qopt${questionCounter}_${i}" placeholder="Option ${i+1}">
                        </div>
                    `).join('')}
                </div>
                <button class="btn btn-danger" onclick="removeQuestion(${questionCounter})">Remove</button>
            `;
            document.getElementById('questionsContainer').appendChild(div);
        }

        function removeQuestion(id) {
            document.getElementById('q' + id).remove();
        }

        async function createExam() {
            const title = document.getElementById('examTitle').value.trim();
            const duration = parseInt(document.getElementById('examDuration').value);

            if (!title || !duration) {
                document.getElementById('examAlert').innerHTML = 
                    '<div class="alert alert-error">Fill all fields</div>';
                return;
            }

            const questions = [];
            for (let i = 1; i <= questionCounter; i++) {
                const qDiv = document.getElementById('q' + i);
                if (!qDiv) continue;

                const qtext = document.getElementById('qtext' + i).value.trim();
                const opts = [0,1,2,3].map(j => 
                    document.getElementById(`qopt${i}_${j}`).value.trim()
                );
                const correct = document.querySelector(`input[name="qcorrect${i}"]:checked`);

                if (!qtext || opts.some(o => !o) || !correct) {
                    document.getElementById('examAlert').innerHTML = 
                        '<div class="alert alert-error">Complete all questions</div>';
                    return;
                }

                questions.push({
                    question: qtext,
                    options: opts,
                    correct: parseInt(correct.value)
                });
            }

            if (questions.length === 0) {
                document.getElementById('examAlert').innerHTML = 
                    '<div class="alert alert-error">Add at least one question</div>';
                return;
            }

            const res = await fetch('/api/admin/exam/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title, duration, questions})
            });

            const data = await res.json();
            
            if (data.success) {
                document.getElementById('examAlert').innerHTML = 
                    '<div class="alert alert-success">Exam created!</div>';
                document.getElementById('examTitle').value = '';
                document.getElementById('examDuration').value = '';
                document.getElementById('questionsContainer').innerHTML = '';
                questionCounter = 0;
                setTimeout(() => switchTab('manage'), 2000);
            }
        }

        async function loadAdminExams() {
            const res = await fetch('/api/admin/exams');
            const exams = await res.json();
            
            const list = document.getElementById('adminExamList');
            list.innerHTML = '';

            for (const [id, exam] of Object.entries(exams)) {
                const div = document.createElement('div');
                div.className = 'question-item';
                div.innerHTML = `
                    <h3>${exam.title}</h3>
                    <p><strong>Duration:</strong> ${exam.duration} min | <strong>Questions:</strong> ${exam.questions.length}</p>
                    <div style="margin-top: 15px;">
                        <button class="btn btn-primary" onclick="viewQuestions('${id}')">View Questions</button>
                        <button class="btn btn-danger" onclick="deleteExam('${id}')">Delete</button>
                    </div>
                    <div id="questions_${id}" class="hidden" style="margin-top: 20px;"></div>
                `;
                list.appendChild(div);
            }
        }

        async function viewQuestions(id) {
            const qDiv = document.getElementById('questions_' + id);
            
            if (!qDiv.classList.contains('hidden')) {
                qDiv.classList.add('hidden');
                return;
            }

            const res = await fetch('/api/admin/exam/' + id);
            const exam = await res.json();
            
            let html = '';
            exam.questions.forEach((q, i) => {
                html += `
                    <div class="question-item">
                        <h4>Q${i+1}: ${q.question}</h4>
                        <div style="margin-left: 20px;">
                            ${q.options.map((opt, j) => 
                                `<div>${j === q.correct ? '✓' : '○'} ${opt} ${j === q.correct ? '<span style="color: #28a745; font-weight: bold;">(Correct)</span>' : ''}</div>`
                            ).join('')}
                        </div>
                    </div>
                `;
            });
            
            qDiv.innerHTML = html;
            qDiv.classList.remove('hidden');
        }

        async function deleteExam(id) {
            if (!confirm('Delete this exam?')) return;

            await fetch('/api/admin/exam/' + id, {method: 'DELETE'});
            loadAdminExams();
        }

        async function loadExams() {
            const res = await fetch('/api/exams');
            const exams = await res.json();
            
            const list = document.getElementById('examList');
            list.innerHTML = '';

            if (Object.keys(exams).length === 0) {
                list.innerHTML = '<p style="text-align: center; color: #666;">No exams available</p>';
                return;
            }

            for (const [key, exam] of Object.entries(exams)) {
                const card = document.createElement('div');
                card.className = 'exam-card';
                card.onclick = () => startExam(key);
                card.innerHTML = `
                    <h3>${exam.title}</h3>
                    <div class="exam-info">
                        <span>📝 ${exam.questions.length} Questions</span>
                        <span>⏱️ ${exam.duration} Minutes</span>
                    </div>
                `;
                list.appendChild(card);
            }
        }

        async function startExam(id) {
            const name = document.getElementById('studentName').value.trim();
            const email = document.getElementById('studentEmail').value.trim();
            const sid = document.getElementById('studentId').value.trim();

            if (!name || !email || !sid) {
                alert('Please fill all student information fields');
                return;
            }

            studentInfo = {name, email, id: sid};

            const res = await fetch('/api/exam/' + id);
            currentExam = await res.json();
            
            currentQuestion = 0;
            answers = {};
            timeLeft = currentExam.duration * 60;
            startTime = Date.now();
            
            hideAll();
            document.getElementById('examContainer').classList.remove('hidden');
            
            displayQuestion();
            startTimer();
        }

        function displayQuestion() {
            const q = currentExam.questions[currentQuestion];
            const progress = ((currentQuestion + 1) / currentExam.questions.length) * 100;
            
            document.getElementById('progressBar').style.width = progress + '%';
            document.getElementById('questionNumber').textContent = 
                `Question ${currentQuestion + 1} of ${currentExam.questions.length}`;
            document.getElementById('questionText').textContent = q.question;
            
            const optsCont = document.getElementById('options');
            optsCont.innerHTML = '';
            
            q.options.forEach((opt, i) => {
                const div = document.createElement('div');
                div.className = 'option';
                if (answers[q.id] === i) div.classList.add('selected');
                div.textContent = opt;
                div.onclick = () => {
                    answers[q.id] = i;
                    displayQuestion();
                };
                optsCont.appendChild(div);
            });
            
            document.getElementById('prevBtn').disabled = currentQuestion === 0;
            
            const isLast = currentQuestion === currentExam.questions.length - 1;
            document.getElementById('nextBtn').classList.toggle('hidden', isLast);
            document.getElementById('submitBtn').classList.toggle('hidden', !isLast);
        }

        function prevQuestion() {
            if (currentQuestion > 0) {
                currentQuestion--;
                displayQuestion();
            }
        }

        function nextQuestion() {
            if (currentQuestion < currentExam.questions.length - 1) {
                currentQuestion++;
                displayQuestion();
            }
        }

        function startTimer() {
            updateTimer();
            timerInterval = setInterval(() => {
                timeLeft--;
                updateTimer();
                
                if (timeLeft <= 60) {
                    document.getElementById('timer').classList.add('warning');
                }
                
                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    submitExam();
                }
            }, 1000);
        }

        function updateTimer() {
            const min = Math.floor(timeLeft / 60);
            const sec = timeLeft % 60;
            document.getElementById('timer').textContent = 
                `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
        }

        async function submitExam() {
            clearInterval(timerInterval);
            
            const timeTaken = Math.floor((Date.now() - startTime) / 1000);
            
            const res = await fetch('/api/submit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    exam: currentExam,
                    answers: answers,
                    timeTaken: timeTaken,
                    student: studentInfo
                })
            });
            
            const result = await res.json();
            showResults(result, timeTaken);
        }

        function showResults(result, timeTaken) {
            hideAll();
            document.getElementById('resultContainer').classList.remove('hidden');
            
            const percentage = Math.round((result.correct / result.total) * 100);
            document.getElementById('score').textContent = `${percentage}%`;
            document.getElementById('totalQuestions').textContent = result.total;
            document.getElementById('correctAnswers').textContent = result.correct;
            document.getElementById('wrongAnswers').textContent = result.wrong;
            
            const min = Math.floor(timeTaken / 60);
            const sec = timeTaken % 60;
            document.getElementById('timeTaken').textContent = `${min}m ${sec}s`;
        }

        function restartExam() {
            location.reload();
        }
    </script>
</body>
</html>
    ''')

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
        session['is_admin'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid credentials'})

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('is_admin', None)
    return jsonify({'success': True})

@app.route('/api/admin/exams')
@admin_required
def get_admin_exams():
    return jsonify(EXAMS)

@app.route('/api/admin/exam/<exam_id>')
@admin_required
def get_admin_exam(exam_id):
    if exam_id not in EXAMS:
        return jsonify({'error': 'Exam not found'}), 404
    return jsonify(EXAMS[exam_id])

@app.route('/api/admin/exam/create', methods=['POST'])
@admin_required
def create_exam():
    data = request.json
    title = data.get('title')
    duration = data.get('duration')
    questions = data.get('questions', [])
    
    if not title or not duration or not questions:
        return jsonify({'success': False, 'error': 'Missing required fields'})
    
    exam_id = title.lower().replace(' ', '_')
    
    for idx, question in enumerate(questions):
        question['id'] = idx + 1
    
    EXAMS[exam_id] = {
        'title': title,
        'duration': duration,
        'questions': questions
    }
    
    return jsonify({'success': True, 'exam_id': exam_id})

@app.route('/api/admin/exam/<exam_id>', methods=['DELETE'])
@admin_required
def delete_exam(exam_id):
    if exam_id in EXAMS:
        del EXAMS[exam_id]
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Exam not found'}), 404

@app.route('/api/exams')
def get_exams():
    return jsonify({
        key: {
            'title': exam['title'],
            'duration': exam['duration'],
            'questions': [{'id': q['id']} for q in exam['questions']]
        }
        for key, exam in EXAMS.items()
    })

@app.route('/api/exam/<exam_id>')
def get_exam(exam_id):
    if exam_id not in EXAMS:
        return jsonify({'error': 'Exam not found'}), 404
    
    exam = EXAMS[exam_id].copy()
    exam['questions'] = [
        {
            'id': q['id'],
            'question': q['question'],
            'options': q['options']
        }
        for q in exam['questions']
    ]
    return jsonify(exam)

@app.route('/api/submit', methods=['POST'])
def submit_exam():
    data = request.json
    exam_questions = next(
        (e['questions'] for e in EXAMS.values() 
         if e['title'] == data['exam']['title']),
        None
    )
    
    if not exam_questions:
        return jsonify({'error': 'Exam not found'}), 404
    
    correct = 0
    total = len(exam_questions)
    
    for question in exam_questions:
        if str(question['id']) in data['answers']:
            if data['answers'][str(question['id'])] == question['correct']:
                correct += 1
    
    return jsonify({
        'correct': correct,
        'wrong': total - correct,
        'total': total,
        'student': data['student']
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
