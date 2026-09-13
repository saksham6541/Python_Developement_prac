import csv
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def hello_world():

    if request.method == "GET":
        return render_template("get_data.html")

    option = request.form.get("ID")
    id_value = request.form.get("id_value")

    if option is None or id_value is None or id_value.strip() == "":
        return render_template("error.html")

    data = []

    with open("data.csv", "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header

        for row in reader:
            data.append(row)

    # ---------------- Student Details ---------------- #

    if option == "student_id":

        student_rows = []
        total = 0

        for row in data:
            if row[0].strip() == id_value.strip():
                student_rows.append(row)
                total += int(row[2])

        if len(student_rows) == 0:
            return render_template("error.html")

        return render_template(
            "student.html",
            student_rows=student_rows,
            total=total
        )

    # ---------------- Course Details ---------------- #

    elif option == "course_id":

        marks = []

        for row in data:
            if row[1].strip() == id_value.strip():
                marks.append(int(row[2]))

        if len(marks) == 0:
            return render_template("error.html")

        average = sum(marks) / len(marks)
        max_marks = max(marks)

        plt.figure()
        plt.hist(marks)
        plt.xlabel("Marks")
        plt.ylabel("Frequency")
        plt.title("Marks Distribution")
        plt.savefig("static/histogram.png")
        plt.close()

        return render_template(
            "courses.html",
            average=average,
            max_marks=max_marks
        )

    return render_template("error.html")


if __name__ == "__main__":
    app.run(debug=True)