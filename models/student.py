# models/student.py
class Student:
    def __init__(self, student_id, first_name, last_name, department, year, credits_taken=0):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.department = department
        self.year = year
        self.credits_taken = credits_taken

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "department": self.department,
            "year": self.year,
            "credits_taken": self.credits_taken
        }