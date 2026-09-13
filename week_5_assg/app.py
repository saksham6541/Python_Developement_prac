from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)


COURSE_VALUE_TO_ID = {
    'course_1': 1,
    'course_2': 2,
    'course_3': 3,
    'course_4': 4,
}
COURSE_ID_TO_VALUE = {v: k for k, v in COURSE_VALUE_TO_ID.items()}


@app.route('/')
def home():
    students = Student.query.all()
    return render_template('index.html', students=students)


@app.route('/student/create', methods=['GET'])
def create_student_form():
    return render_template('create.html')


@app.route('/student/create', methods=['POST'])
def create_student():
    roll = request.form.get('roll', '').strip()
    f_name = request.form.get('f_name', '').strip()
    l_name = request.form.get('l_name', '').strip()
    selected_courses = request.form.getlist('courses')

    existing = Student.query.filter_by(roll_number=roll).first()
    if existing:
        return render_template('exists.html')

    student = Student(roll_number=roll, first_name=f_name, last_name=l_name)
    db.session.add(student)
    db.session.commit()

    for course_value in selected_courses:
        course_id = COURSE_VALUE_TO_ID.get(course_value)
        if course_id:
            enrollment = Enrollment(estudent_id=student.student_id, ecourse_id=course_id)
            db.session.add(enrollment)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/student/<int:student_id>')
def student_details(student_id):
    student = Student.query.get_or_404(student_id)
    enrollments = Enrollment.query.filter_by(estudent_id=student_id).all()
    courses = []
    for e in enrollments:
        course = Course.query.get(e.ecourse_id)
        if course:
            courses.append(course)
    return render_template('student.html', student=student, courses=courses)


@app.route('/student/<int:student_id>/update', methods=['GET'])
def update_student_form(student_id):
    student = Student.query.get_or_404(student_id)
    enrollments = Enrollment.query.filter_by(estudent_id=student_id).all()
    enrolled_values = {COURSE_ID_TO_VALUE.get(e.ecourse_id) for e in enrollments}
    return render_template('update.html', student=student, enrolled_values=enrolled_values)


@app.route('/student/<int:student_id>/update', methods=['POST'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)

    f_name = request.form.get('f_name', '').strip()
    l_name = request.form.get('l_name', '').strip()
    selected_courses = request.form.getlist('courses')

    student.first_name = f_name
    student.last_name = l_name
    db.session.commit()

    # Remove existing enrollments and re-create based on the submitted form
    Enrollment.query.filter_by(estudent_id=student_id).delete()
    db.session.commit()

    for course_value in selected_courses:
        course_id = COURSE_VALUE_TO_ID.get(course_value)
        if course_id:
            enrollment = Enrollment(estudent_id=student_id, ecourse_id=course_id)
            db.session.add(enrollment)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/student/<int:student_id>/delete', methods=['GET'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)

    Enrollment.query.filter_by(estudent_id=student_id).delete()
    db.session.delete(student)
    db.session.commit()

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)