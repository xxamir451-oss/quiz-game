import json
import random
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# بارگذاری سوالات از فایل
with open('questions_generated.json', 'r', encoding='utf-8') as f:
    QUESTIONS = json.load(f)

HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>کوییز هوشمند</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: Tahoma, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
        }
        .container {
            width: 100%;
            max-width: 500px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 25px;
        }
        h1 { text-align: center; color: #333; margin-bottom: 20px; font-size: 24px; }
        h2 { text-align: center; color: #667eea; margin-bottom: 15px; font-size: 18px; }
        .info { display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 14px; color: #666; }
        .question {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            font-size: 17px;
            font-weight: bold;
            color: #333;
            text-align: center;
        }
        .options { display: flex; flex-direction: column; gap: 10px; }
        .option {
            padding: 14px;
            background: #f0f0f0;
            border: 2px solid #ddd;
            border-radius: 12px;
            cursor: pointer;
            font-size: 15px;
            text-align: center;
            transition: all 0.2s;
        }
        .option:hover { background: #e0e0e0; }
        .option.correct { background: #4CAF50; color: white; border-color: #4CAF50; }
        .option.wrong { background: #f44336; color: white; border-color: #f44336; }
        .option.disabled { pointer-events: none; }
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
            font-family: Tahoma;
        }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
        .grid-item {
            padding: 15px;
            background: #f0f0f0;
            border: 2px solid #ddd;
            border-radius: 12px;
            cursor: pointer;
            font-size: 14px;
            text-align: center;
            transition: all 0.2s;
        }
        .grid-item:hover { background: #e0e0e0; }
        .grid-item.selected { background: #667eea; color: white; border-color: #667eea; }
        .result { text-align: center; padding: 20px; }
        .result h2 { color: #333; margin-bottom: 15px; }
        .result .score { font-size: 48px; color: #667eea; font-weight: bold; }
        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 14px;
            border: 2px solid #ddd;
            border-radius: 12px;
            font-size: 15px;
            font-family: Tahoma;
            text-align: center;
            outline: none;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 کوییز هوشمند</h1>
        <div id="content">
            <p style="text-align:center; margin-bottom:20px; color:#666;">برای شروع، اسمت رو بنویس:</p>
            <input type="text" id="playerName" placeholder="اسمت...">
            <button class="btn" onclick="showCategories()">ادامه</button>
        </div>
    </div>

    <script>
        let currentQuestion = 0;
        let score = 0;
        let questions = [];
        let playerName = '';
        let selectedCategory = '';
        let selectedLevel = '';
        let questionCount = 5;

        function showCategories() {
            playerName = document.getElementById('playerName').value.trim();
            if (!playerName) { alert('اسمت رو بنویس!'); return; }
            
            const categories = ['علم', 'جغرافیا', 'تاریخ', 'ادبیات', 'ریاضی', 'سلامت', 'فناوری', 'انگلیسی', 'معلومات عمومی'];
            document.getElementById('content').innerHTML = `
                <h2>📚 دسته‌بندی رو انتخاب کن:</h2>
                <div class="grid" id="catGrid">
                    ${categories.map(c => `<div class="grid-item" onclick="selectCategory(this, '${c}')">${c}</div>`).join('')}
                </div>
            `;
        }

        function selectCategory(el, cat) {
            document.querySelectorAll('#catGrid .grid-item').forEach(i => i.classList.remove('selected'));
            el.classList.add('selected');
            selectedCategory = cat;
            setTimeout(showLevels, 300);
        }

        function showLevels() {
            const levels = ['آسان', 'متوسط', 'سخت'];
            document.getElementById('content').innerHTML = `
                <h2>🎯 سطح رو انتخاب کن:</h2>
                <div class="grid" id="lvlGrid">
                    ${levels.map(l => `<div class="grid-item" onclick="selectLevel(this, '${l}')">${l}</div>`).join('')}
                </div>
            `;
        }

        function selectLevel(el, lvl) {
            document.querySelectorAll('#lvlGrid .grid-item').forEach(i => i.classList.remove('selected'));
            el.classList.add('selected');
            selectedLevel = lvl;
            setTimeout(showQuestionCount, 300);
        }

        function showQuestionCount() {
            document.getElementById('content').innerHTML = `
                <h2>🔢 چند سوال می‌خوای؟</h2>
                <p style="text-align:center; color:#666; margin-bottom:15px;">از ۱ تا ۱۰۰ انتخاب کن</p>
                <input type="number" id="qCount" min="1" max="100" value="5">
                <button class="btn" onclick="startGame()">شروع بازی</button>
            `;
        }

        async function startGame() {
            const countInput = document.getElementById('qCount').value;
            questionCount = parseInt(countInput);
            
            if (questionCount < 1 || questionCount > 100) {
                alert('لطفاً عددی بین ۱ تا ۱۰۰ وارد کن!');
                return;
            }
            
            const res = await fetch('/get-questions', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    category: selectedCategory, 
                    level: selectedLevel,
                    count: questionCount
                })
            });
            const data = await res.json();
            questions = data.questions;
            currentQuestion = 0;
            score = 0;
            showQuestion();
        }

        function showQuestion() {
            if (currentQuestion >= questions.length) {
                showResult();
                return;
            }
            const q = questions[currentQuestion];
            document.getElementById('content').innerHTML = `
                <div class="info">
                    <span>${selectedCategory} - ${selectedLevel}</span>
                    <span>سوال ${currentQuestion + 1} از ${questions.length}</span>
                    <span>امتیاز: ${score}</span>
                </div>
                <div class="question">${q.q}</div>
                <div class="options" id="options">
                    ${q.options.map(opt => `<div class="option" onclick="checkAnswer(this, '${opt}', '${q.answer}')">${opt}</div>`).join('')}
                </div>
            `;
        }

        function checkAnswer(el, selected, correct) {
            const options = document.querySelectorAll('.option');
            options.forEach(o => o.classList.add('disabled'));
            
            if (selected === correct) {
                el.classList.add('correct');
                score += 10;
            } else {
                el.classList.add('wrong');
                options.forEach(o => {
                    if (o.textContent.trim() === correct) o.classList.add('correct');
                });
            }
            
            setTimeout(() => {
                currentQuestion++;
                showQuestion();
            }, 1500);
        }

        function showResult() {
            const maxScore = questions.length * 10;
            document.getElementById('content').innerHTML = `
                <div class="result">
                    <h2>🎉 ${playerName} جان، تموم شد!</h2>
                    <div class="score">${score}</div>
                    <p style="color:#666; margin:15px 0;">امتیازت از ${maxScore}</p>
                    <p style="color:#667eea; margin-bottom:15px;">درس: ${selectedCategory}</p>
                    <button class="btn" onclick="location.reload()">دوباره بازی کن</button>
                </div>
            `;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/get-questions', methods=['POST'])
def get_questions():
    data = request.get_json()
    category = data.get('category', 'علم')
    level = data.get('level', 'آسان')
    count = data.get('count', 5)
    
    all_q = QUESTIONS.get(category, {}).get(level, [])
    
    if count > len(all_q):
        count = len(all_q)
    
    if count == 0:
        return jsonify({'questions': []})
    
    selected = random.sample(all_q, count)
    for q in selected:
        random.shuffle(q['options'])
    
    return jsonify({
        'category': category,
        'level': level,
        'questions': selected
    })

if __name__ == '__main__':
    print("🎮 بازی کوییز روی http://localhost:5000 اجرا شد")
    app.run(host='0.0.0.0', port=5000)
