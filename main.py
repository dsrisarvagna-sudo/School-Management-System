import json
from pathlib import Path
from abc import ABC, abstractmethod

DB="school_data.json"
data={"students":[],"teachers":[]}

if Path(DB).exists():
    with open(DB,"r") as f:
        c=f.read()
        if c: data=json.loads(c)

def save():
    with open(DB,"w") as f:
        json.dump(data,f,indent=4)

class Person(ABC):
    @abstractmethod
    def get_role(self): pass
    @abstractmethod
    def register(self): pass
    @abstractmethod
    def show_details(self): pass

    @staticmethod
    def validate_email(e):
        return "@" in e and "." in e

class Student(Person):
    def get_role(self): return "student"

    def register(self):
        name=input("name: ")
        a=input("age: ")
        email=input("email: ")
        roll=input("roll no: ")

        if not Person.validate_email(email):
            print("invalid email"); return
        if not a.isdigit():
            print("invalid age"); return

        for s in data["students"]:
            if s["roll_no"]==roll:
                print("already exists"); return

        data["students"].append({"name":name,"age":int(a),"email":email,"roll_no":roll,"grades":{}})
        save()
        print(f"student {name} registered")

    def show_details(self):
        if not data["students"]:
            print("no students yet"); return
        for s in data["students"]:
            print(f"{s['name']} | age {s['age']} | roll {s['roll_no']} | grades {s['grades']}")

    def add_grade(self):
        roll_no=input("tell the roll number :- ")
        subject=input("Subject : ")
        marks=float(input("Marks : "))

        for i in data['students']:
            if i["roll_no"]==roll_no:
                i['grades'][subject]=marks
                save()
                print("grade added successfully")
                return
        print("student not found")

class Teacher(Person):
    def get_role(self): return "teacher"

    def register(self):
        name=input("name: ")
        a=input("age: ")
        email=input("email: ")
        subj=input("subject: ")
        emp_id=input("employee id: ")

        if not Person.validate_email(email):
            print("invalid email"); return
        if not a.isdigit():
            print("invalid age"); return

        for t in data["teachers"]:
            if t["emp_id"]==emp_id:
                print("already exists"); return

        data["teachers"].append({"name":name,"age":int(a),"email":email,"subject":subj,"emp_id":emp_id})
        save()
        print(f"teacher {name} registered")

    def show_details(self):
        if not data["teachers"]:
            print("no teachers yet"); return
        for t in data["teachers"]:
            print(f"{t['name']} | age {t['age']} | subj {t['subject']} | id {t['emp_id']}")

def main():
    s=Student(); t=Teacher()
    while True:
        print("\n1.Register Student 2.Register Teacher 3.Show Students 4.Show Teachers 5.Add Grade 6.Exit")
        ch=input("choice: ")
        if ch=="1": s.register()
        elif ch=="2": t.register()
        elif ch=="3": s.show_details()
        elif ch=="4": t.show_details()
        elif ch=="5": s.add_grade()
        elif ch=="6": break
        else: print("invalid choice")

if __name__=="__main__":
    main()


        
