from flask import Flask, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///api_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)


# ------------------- Models -------------------

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String, nullable=False)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_description = db.Column(db.String)


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)


class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)


# ------------------- Helpers -------------------

def course_to_dict(course):
    return {
        'course_id': course.course_id,
        'course_name': course.course_name,
        'course_code': course.course_code,
        'course_description': course.course_description,
    }


def student_to_dict(student):
    return {
        'student_id': student.student_id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'roll_number': student.roll_number,
    }


def enrollment_to_dict(enrollment):
    return {
        'enrollment_id': enrollment.enrollment_id,
        'student_id': enrollment.student_id,
        'course_id': enrollment.course_id,
    }


def error_response(error_code, error_message):
    return {'error_code': error_code, 'error_message': error_message}, 400


# ------------------- Course Resources -------------------

class CourseAPI(Resource):
    def get(self, course_id):
        course = Course.query.get(course_id)
        if course is None:
            return {'error_message': 'Course not found'}, 404
        return course_to_dict(course), 200

    def put(self, course_id):
        course = Course.query.get(course_id)
        if course is None:
            return {'error_message': 'Course not found'}, 404

        data = request.get_json(force=True, silent=True) or {}

        course_name = data.get('course_name')
        course_code = data.get('course_code')

        if course_name is None or course_name == '':
            return error_response('COURSE001', 'Course Name is required')
        if course_code is None or course_code == '':
            return error_response('COURSE002', 'Course Code is required')

        course.course_name = course_name
        course.course_code = course_code
        course.course_description = data.get('course_description')

        db.session.commit()
        return course_to_dict(course), 200

    def delete(self, course_id):
        course = Course.query.get(course_id)
        if course is None:
            return {'error_message': 'Course not found'}, 404

        db.session.delete(course)
        db.session.commit()
        return '', 200


class CourseListAPI(Resource):
    def post(self):
        data = request.get_json(force=True, silent=True) or {}

        course_name = data.get('course_name')
        course_code = data.get('course_code')

        if course_name is None or course_name == '':
            return error_response('COURSE001', 'Course Name is required')
        if course_code is None or course_code == '':
            return error_response('COURSE002', 'Course Code is required')

        existing = Course.query.filter_by(course_code=course_code).first()
        if existing is not None:
            return {'error_message': 'course_code already exist'}, 409

        course = Course(
            course_name=course_name,
            course_code=course_code,
            course_description=data.get('course_description'),
        )
        db.session.add(course)
        db.session.commit()
        return course_to_dict(course), 201


# ------------------- Student Resources -------------------

class StudentAPI(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if student is None:
            return {'error_message': 'Student not found'}, 404
        return student_to_dict(student), 200

    def put(self, student_id):
        student = Student.query.get(student_id)
        if student is None:
            return {'error_message': 'Student not found'}, 404

        data = request.get_json(force=True, silent=True) or {}

        roll_number = data.get('roll_number')
        first_name = data.get('first_name')

        if roll_number is None or roll_number == '':
            return error_response('STUDENT001', 'Roll Number required')
        if first_name is None or first_name == '':
            return error_response('STUDENT002', 'First Name is required')

        student.roll_number = roll_number
        student.first_name = first_name
        student.last_name = data.get('last_name')

        db.session.commit()
        return student_to_dict(student), 200

    def delete(self, student_id):
        student = Student.query.get(student_id)
        if student is None:
            return {'error_message': 'Student not found'}, 404

        db.session.delete(student)
        db.session.commit()
        return '', 200


class StudentListAPI(Resource):
    def post(self):
        data = request.get_json(force=True, silent=True) or {}

        roll_number = data.get('roll_number')
        first_name = data.get('first_name')

        if roll_number is None or roll_number == '':
            return error_response('STUDENT001', 'Roll Number required')
        if first_name is None or first_name == '':
            return error_response('STUDENT002', 'First Name is required')

        existing = Student.query.filter_by(roll_number=roll_number).first()
        if existing is not None:
            return {'error_message': 'Student already exist'}, 409

        student = Student(
            roll_number=roll_number,
            first_name=first_name,
            last_name=data.get('last_name'),
        )
        db.session.add(student)
        db.session.commit()
        return student_to_dict(student), 201


# ------------------- Enrollment Resources -------------------

class StudentCourseAPI(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if student is None:
            return error_response('ENROLLMENT002', 'Student does not exist.')

        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        if not enrollments:
            return {'error_message': 'Student is not enrolled in any course'}, 404

        return [enrollment_to_dict(e) for e in enrollments], 200

    def post(self, student_id):
        student = Student.query.get(student_id)
        if student is None:
            return {'error_message': 'Student not found'}, 404

        data = request.get_json(force=True, silent=True) or {}
        course_id = data.get('course_id')

        course = Course.query.get(course_id) if course_id is not None else None
        if course is None:
            return error_response('ENROLLMENT001', 'Course does not exist')

        enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()

        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        return [enrollment_to_dict(e) for e in enrollments], 201


class StudentCourseDeleteAPI(Resource):
    def delete(self, student_id, course_id):
        student = Student.query.get(student_id)
        if student is None:
            return error_response('ENROLLMENT002', 'Student does not exist.')

        course = Course.query.get(course_id)
        if course is None:
            return error_response('ENROLLMENT001', 'Course does not exist')

        enrollment = Enrollment.query.filter_by(
            student_id=student_id, course_id=course_id
        ).first()
        if enrollment is None:
            return {'error_message': 'Enrollment for the student not found'}, 404

        db.session.delete(enrollment)
        db.session.commit()
        return '', 200


# ------------------- Routes -------------------

api.add_resource(CourseListAPI, '/api/course')
api.add_resource(CourseAPI, '/api/course/<int:course_id>')
api.add_resource(StudentListAPI, '/api/student')
api.add_resource(StudentAPI, '/api/student/<int:student_id>')
api.add_resource(StudentCourseAPI, '/api/student/<int:student_id>/course')
api.add_resource(StudentCourseDeleteAPI, '/api/student/<int:student_id>/course/<int:course_id>')


if __name__ == '__main__':
    app.run(debug=True)