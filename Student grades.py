#Student grades
class Student:
    def __init__(self,name,grades):
        self.name=name
        self.grades=grades
    def best(self):
        subject= max(self.grades,key=self.grades.get)
        return subject,self.grades[subject]
    def worst(self):
        subject= min(self.grades,key=self.grades.get)
        return subject,self.grades[subject]
    def average(self):
        return sum(self.grades.values())/len(self.grades)
name=input("Name: ")
grades={}
subjects=["Math","Physics","English","History","Chemistry"]
for subject in subjects:
    grade=int(input(f"{subject}: "))
    grades[subject]=grade
s=Student(name,grades)
best_subject, best_grade = s.best()
worst_subject, worst_grade = s.worst()
print(f"Best: {best_subject}({best_grade})")
print(f"Worst: {worst_subject}({worst_grade})")
print(f"Average: {s.average():.2f}")
