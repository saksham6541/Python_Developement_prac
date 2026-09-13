import sys
import csv
import matplotlib.pyplot as plt
from jinja2 import Template


student_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Details</title>
</head>
<body>

<h1>Student Details</h1>

<table border="1">
<tr>
    <th>Student ID</th>
    <th>Course ID</th>
    <th>Marks</th>
</tr>

{% for row in student_rows %}
<tr>
    <td>{{ row[0] }}</td>
    <td>{{ row[1] }}</td>
    <td>{{ row[2] }}</td>
</tr>
{% endfor %}

<tr>
    <td colspan="2"><b>Total Marks</b></td>
    <td>{{ total }}</td>
</tr>

</table>

</body>
</html>
"""


course_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Course Details</title>
</head>
<body>

<h1>Course Details</h1>

<table border="1">
<tr>
    <th>Average Marks</th>
    <th>Maximum Marks</th>
</tr>

<tr>
    <td>{{ avg }}</td>
    <td>{{ max_marks }}</td>
</tr>

</table>

<br>

<img src="histogram.png">

</body>
</html>
"""


error_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
</head>
<body>

<h1>Wrong Inputs</h1>

<p>Something went wrong.</p>

</body>
</html>
"""


if len(sys.argv) != 3:
    template = Template(error_template)
    with open("output.html", "w") as file:
        file.write(template.render())
    sys.exit()

option = sys.argv[1]
id_value = sys.argv[2]

data = []

with open("data.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        row = [x.strip() for x in row]
        data.append(row)



if option == "-s":

    student_rows = []
    total = 0

    for row in data:
        if row[0] == id_value:
            student_rows.append(row)
            total += int(row[2])

    if len(student_rows) == 0:
        template = Template(error_template)

        with open("output.html", "w") as file:
            file.write(template.render())

        sys.exit()

    template = Template(student_template)

    output = template.render(
        student_rows=student_rows,
        total=total
    )

    with open("output.html", "w") as file:
        file.write(output)



elif option == "-c":

    marks = []

    for row in data:
        if row[1] == id_value:
            marks.append(int(row[2]))

    if len(marks) == 0:
        template = Template(error_template)

        with open("output.html", "w") as file:
            file.write(template.render())

        sys.exit()

    avg = sum(marks) / len(marks)
    max_marks = max(marks)

    plt.figure(figsize=(6,4))
    plt.hist(marks, bins='auto')
    plt.xlabel("Marks")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("histogram.png")
    plt.close()

    template = Template(course_template)

    output = template.render(
        avg=round(avg, 2),
        max_marks=max_marks
    )

    with open("output.html", "w") as file:
        file.write(output)


else:

    template = Template(error_template)

    with open("output.html", "w") as file:
        file.write(template.render())