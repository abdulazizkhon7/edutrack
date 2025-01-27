from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import cast, Date
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, ClassLog, DailyLog  # models.py dan import qiling
from flask_migrate import Migrate
from flask import flash




app = Flask(__name__)
# Flask dasturini sozlash
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edutrack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'maxfiy_kalit'


# Migrate instansiyasini yarating
migrate = Migrate(app, db)



# Ma'lumotlar bazasi va login tizimini ulash
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Foydalanuvchini yuklash funksiyasi
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




# Kirish sahifasi
@app.route('/', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            error_message = "ユーザー名またはパスワードが正しくありません."
    return render_template('login.html', error_message=error_message)

# Ro'yxatdan o'tish sahifasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Parol uzunligini tekshirish
        if len(password) < 8:
            error_message = "パスワードは8文字以上である必要があります！"
            return render_template('register.html', error_message=error_message)

        # Parolni hashlash va foydalanuvchini ro'yxatdan o'tkazish
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role == "admin":
        students = User.query.filter_by(role="student").all()
        student_names = [student.username for student in students]
        
        return render_template('admin_dashboard.html', student_names=student_names, )
    else:
        return render_template('student_dashboard.html')

@app.route('/view_class_logs', methods=['GET'])
@login_required
def view_class_logs():
    search_date = request.args.get('search_date')  # Sana qidiruvi

    query = ClassLog.query  # Asosiy so‘rov

    # Sana bo‘yicha filtr
    if search_date:
        try:
            search_date_obj = datetime.strptime(search_date, '%Y-%m-%d').date()
            query = query.filter(ClassLog.date == search_date_obj)  # To‘g‘ridan-to‘g‘ri qiyoslash
        except ValueError:
            return "日付の形式が正しくありません！", 400

    # Hamma yozuvlarni admin va talaba huquqiga qarab ko‘rsatish
    if current_user.role == "admin":
        logs = query.all()  # Admin uchun barcha yozuvlar
    else:
        logs = query.all()  # Talabalar uchun ham barcha yozuvlar (barchasini ko‘rsatish)

    # Foydalanuvchi nomlarini va attendance ma'lumotlarini qo‘shamiz
    enriched_logs = []
    for log in logs:
        user = User.query.get(log.user_id)
        enriched_logs.append({
            'log': log,
            'username': user.username if user else 'エラー：不明な問題が発生しました。',
            'attendance': log.attendance  # Davomat ma'lumoti
        })

    return render_template('view_class_logs.html', logs=enriched_logs)

@app.route('/edit_class_log/<int:log_id>', methods=['GET', 'POST'])
@login_required
def edit_class_log(log_id):
    # Logni topish
    log = ClassLog.query.get_or_404(log_id)

    # Faqat talaba o‘z yozuvini o‘zgartira oladi
    if current_user.role == "student" and log.user_id != current_user.id:
        return "この記録を編集する権限がありません！", 403

    if request.method == 'POST':
        log.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        log.period = request.form['period']
        log.subject = request.form['subject']
        log.teacher = request.form['teacher']
        log.content = request.form['content']
        log.attendance = request.form['attendance']
        db.session.commit()
        return redirect(url_for('view_class_logs'))

    return render_template('edit_class_log.html', log=log)

@app.route('/students')
@login_required
def view_students():
    if current_user.role != "admin":
        return "このページにアクセスする権限がありません！", 403
    students = User.query.filter_by(role="student").all()
    return render_template('admin_students.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != "admin":
        return "このページにアクセスする権限がありません！", 403

    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_student = User(username=username, password=password, role="student")
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('view_students'))

    return render_template('add_student.html')

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    if current_user.role != "admin":
        return "このページにアクセスする権限がありません！", 403

    student = User.query.get_or_404(student_id)

    if request.method == 'POST':
        student.username = request.form['username']
        if request.form['password']:
            student.password = generate_password_hash(request.form['password'])
        db.session.commit()
        return redirect(url_for('view_students'))

    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<int:student_id>')
@login_required
def delete_student(student_id):
    if current_user.role != "admin":
        return "このページにアクセスする権限がありません！", 403

    student = User.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('view_students'))

@app.route('/guide')
@login_required
def guide():
    return render_template('guide.html')

app.secret_key = 'maxfiy_kalit'  # Sessiya uchun kalit

@app.route('/add_notes', methods=['GET', 'POST'])
@login_required
def add_notes():
    if request.method == 'POST':
        date = request.form['date']
        after_class_notes = request.form['after_class_notes']
        impressions = request.form['impressions']

        new_note = DailyLog(
            date=datetime.strptime(date, '%Y-%m-%d'),
            after_class_notes=after_class_notes,
            impressions=impressions,
            user_id=current_user.id
        )
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('view_notes'))

    return render_template('add_notes.html')

@app.route('/view_notes', methods=['GET'])
@login_required
def view_notes():
    search_date = request.args.get('search_date')  # Qidiruv uchun sana

    # Asosiy so‘rov
    query = DailyLog.query

    # Sana bo‘yicha filtr qo‘llash
    if search_date:
        try:
            search_date_obj = datetime.strptime(search_date, '%Y-%m-%d').date()
            query = query.filter(DailyLog.date == search_date_obj)
        except ValueError:
            flash('日付の形式が正しくありません！', 'danger')
            return redirect(url_for('view_notes'))

    # Admin barcha yozuvlarni ko‘radi, talabalar esa barcha yozuvlarni ko‘radi
    if current_user.role == 'admin':
        logs = query.all()  # Admin uchun barcha yozuvlar
    else:
        logs = query.all()  # Talabalar ham barcha yozuvlarni ko‘radi

    # Foydalanuvchi nomini yozuvlar bilan birga jo‘natish
    enriched_logs = []
    for log in logs:
        user = User.query.get(log.user_id)
        enriched_logs.append({
            'log': log,
            'username': user.username if user else 'Noma’lum'
        })

    return render_template('view_notes.html', logs=enriched_logs)

@app.route('/view_daily_logs', methods=['GET'])
@login_required
def view_daily_logs():
    if current_user.role == "admin":
        logs = DailyLog.query.all()  # Admin uchun barcha yozuvlar
    else:
        logs = DailyLog.query.filter_by(user_id=current_user.id).all()  # Talaba uchun faqat o‘z yozuvlari

    return render_template('view_daily_logs.html', logs=logs)


@app.route('/edit_note/<int:log_id>', methods=['GET', 'POST'])
@login_required
def edit_note(log_id):
    log = DailyLog.query.get_or_404(log_id)

    # Faqat admin yoki yozuv egasi tahrirlashi mumkin
    if current_user.role != "admin" and log.user_id != current_user.id:
        return "この記録を編集する権限がありません！", 403

    if request.method == 'POST':
        log.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        log.after_class_notes = request.form['after_class_notes']
        log.impressions = request.form['impressions']

        db.session.commit()
        return redirect(url_for('view_notes'))

    return render_template('edit_note.html', log=log)

@app.route('/add_class_log', methods=['GET', 'POST'])
@login_required
def add_class_log():
    if request.method == 'POST':
        # Kiritilgan qiymatlarni olish
        date = request.form['date']
        period = request.form['period']
        subject = request.form['subject']
        teacher = request.form['teacher']
        content = request.form['content']
        attendance = request.form.get('attendance', '')  # Bo'sh bo'lishi mumkin

        # Yangi yozuvni yaratish
        new_log = ClassLog(
            date=datetime.strptime(date, '%Y-%m-%d'),
            period=period,
            subject=subject,
            teacher=teacher,
            content=content,
            attendance=attendance,
            user_id=current_user.id
        )
        db.session.add(new_log)
        db.session.commit()
        return redirect(url_for('view_class_logs'))
    return render_template('add_class_log.html')

@app.route('/test_view_notes', methods=['GET'])
def test_view_notes():
    logs = DailyLog.query.all()
    for log in logs:
        print(f"Sana: {log.date}, Foydalanuvchi: {log.user.username if log.user else 'Noma’lum'}")
    return "Test bajarildi"

@app.route('/admin_dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for('dashboard'))  # Faqat admin uchun
    return render_template('admin_dashboard.html')

@app.route('/delete_note/<int:log_id>', methods=['POST'])
@login_required
def delete_note(log_id):
    # Yozuvni topish
    log = DailyLog.query.get_or_404(log_id)

    # Faqat yozuv egasi yoki admin o‘chirishi mumkin
    if log.user_id != current_user.id and current_user.role != 'admin':
        flash('Siz bu yozuvni o‘chirish huquqiga ega emassiz!', 'danger')
        return redirect(url_for('view_notes'))

    db.session.delete(log)
    db.session.commit()
    flash('Yozuv muvaffaqiyatli o‘chirildi!', 'success')
    return redirect(url_for('view_notes'))


@app.route('/delete_class_log/<int:log_id>', methods=['POST'])
@login_required
def delete_class_log(log_id):
    # Sinf yozuvini topish
    log = ClassLog.query.get_or_404(log_id)

    # Faqat yozuv egasi yoki admin o‘chirishi mumkin
    if log.user_id != current_user.id and current_user.role != 'admin':
        flash('Siz bu yozuvni o‘chirish huquqiga ega emassiz!', 'danger')
        return redirect(url_for('view_class_logs'))

    db.session.delete(log)
    db.session.commit()
    flash('Yozuv muvaffaqiyatli o‘chirildi!', 'success')
    return redirect(url_for('view_class_logs'))

# Chiqish
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Ma'lumotlar bazasini yaratish
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(host='0.0.0.0', port=5000)
