import sys
import csv
import matplotlib.pyplot as plt

from jinja2 import Environment, FileSystemLoader


option= sys.argv[1]
id_value=sys.argv[2]

data=[]

with open("data.csv","r") as file:
    reader = csv.reader(file)

    next(reader)

    for row in reader:
        data.append(row)
    

students_row=[]

total =0

if option == "-s":
    for row in data:
        if(row[0]== id_value):
            students_row.append(row)
            total+=int(row[2])
    
    if len(students_row) == 0:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("error.html")
        output = template.render()
        with open("output.html", "w") as file:
            file.write(output)
        exit()

    env = Environment(loader = FileSystemLoader("templates"))
    tempelate = env.get_template("student.html")

    output = tempelate.render(student_rows=students_row,total=total)

    with open("output.html","w") as file:
        file.write(output)
elif option == "-c":
    c=0
    total=0
    max_marks=0
    for row in data:
        if(row[1].strip()==id_value):
            total+=int(row[2].strip())
            c+=1
            if(int(row[2])>max_marks):
                max_marks=int(row[2])
    if c==0:
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("error.html")
        output = template.render()
        with open("output.html", "w") as file:
            file.write(output)
        exit()
    
    avg=total/c

    marks=[]

    for row in data:
        if row[1].strip()==id_value:
            marks.append(int(row[2]))
    

    plt.hist(marks)
    plt.xlabel("Marks")
    plt.ylabel("Frequency")
    plt.savefig("histogram.png")
    plt.close()
    
    env = Environment(loader=FileSystemLoader("templates"))
    tempelate=env.get_template("courses.html")

    output=tempelate.render(avg=avg,max_marks=max_marks)

    with open("output.html","w") as file:
        file.write(output)
