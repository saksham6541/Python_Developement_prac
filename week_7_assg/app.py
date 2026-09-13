from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'
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


@app.route('/')
def home():
    students = db.session.query(Student).all()
    return render_template('index.html', students=students)


@app.route('/student/create', methods=['GET'])
def create_student_form():
    return render_template("create.html")


@app.route('/student/create', methods=['POST'])
def create_student():
    roll = request.form.get('roll', '').strip()
    f_name = request.form.get('f_name', '').strip()
    l_name = request.form.get('l_name', '').strip()

    existing = Student.query.filter_by(roll_number=roll).first()
    if existing:
        return render_template('exists.html')

    student = Student(
        roll_number=roll,
        first_name=f_name,
        last_name=l_name
    )

    db.session.add(student)
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

    student = db.session.get(Student, student_id)

    if student is None:
        return "Student not found", 404

    courses = db.session.query(Course).all()

    enrollments = db.session.query(Enrollment).filter_by(
        estudent_id=student_id
    ).all()

    enrolled_courses = {e.ecourse_id for e in enrollments}

    return render_template(
        "update.html",
        student=student,
        courses=courses,
        enrolled_courses=enrolled_courses
    )


@app.route('/student/<int:student_id>/update', methods=['POST'])
def update_student(student_id):

    student = Student.query.get_or_404(student_id)

    student.first_name = request.form.get('f_name', '').strip()
    student.last_name = request.form.get('l_name', '').strip()

    selected_course = request.form.get('course')

    db.session.commit()

    # Previous enrollments must persist; only add the newly selected
    # course if the student isn't already enrolled in it.
    if selected_course:
        selected_course_id = int(selected_course)
        already_enrolled = Enrollment.query.filter_by(
            estudent_id=student_id,
            ecourse_id=selected_course_id
        ).first()
        if not already_enrolled:
            enrollment = Enrollment(
                estudent_id=student_id,
                ecourse_id=selected_course_id
            )
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


@app.route('/student/<int:student_id>/withdraw/<int:course_id>', methods=['GET'])
def withdraw_course(student_id, course_id):
    Student.query.get_or_404(student_id)

    Enrollment.query.filter_by(
        estudent_id=student_id,
        ecourse_id=course_id
    ).delete()
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/courses')
def courses():
    all_courses = db.session.query(Course).all()
    return render_template('courses.html', courses=all_courses)


@app.route('/course/create', methods=["GET"])
def create_course_form():
    return render_template("create_course.html")


@app.route('/course/create', methods=['POST'])
def create_course():

    code = request.form.get('code').strip()
    name = request.form.get('c_name').strip()
    desc = request.form.get('desc', '').strip()

    existing = db.session.query(Course).filter_by(course_code=code).first()

    if existing:
        return render_template("exists.html")
    course = Course(
        course_code=code,
        course_name=name,
        course_description=desc
    )
    db.session.add(course)
    db.session.commit()

    return redirect(url_for("courses"))


@app.route('/course/<int:course_id>')
def course_details(course_id):
    course = db.session.get(Course, course_id)

    if course is None:
        return "Course not Found", 404
    students = []
    enrollments = db.session.query(Enrollment).filter_by(ecourse_id=course_id).all()
    for e in enrollments:
        student = db.session.get(Student, e.estudent_id)
        if student:
            students.append(student)
    return render_template(
        "course.html",
        course=course,
        students=students
    )


@app.route('/course/<int:course_id>/update', methods=["GET"])
def update_course_form(course_id):
    course = db.session.get(Course, course_id)

    if course is None:
        return "Course Not Found", 404

    return render_template("update_course.html", course=course)


@app.route('/course/<int:course_id>/update', methods=["POST"])
def update_course(course_id):

    course = db.session.get(Course, course_id)

    if course is None:
        return "Course not found", 404

    code = request.form.get("code").strip()
    name = request.form.get("c_name").strip()
    desc = request.form.get("desc", "").strip()

    existing = db.session.query(Course).filter(
        Course.course_code == code,
        Course.course_id != course_id
    ).first()

    if existing:
        return render_template("exists.html")

    course.course_code = code
    course.course_name = name
    course.course_description = desc

    db.session.commit()

    return redirect(url_for("courses"))


@app.route('/course/<int:course_id>/delete')
def delete_course(course_id):
    course = db.session.get(Course, course_id)

    if course is None:
        return "Course Not Found", 404
    db.session.query(Enrollment).filter_by(
        ecourse_id=course_id
    ).delete()

    db.session.delete(course)
    db.session.commit()

    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)