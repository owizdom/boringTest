# models/course.py
class Course:
    def __init__(self, course_id, course_code, course_name, department, credits, prerequisite_id=None, max_seats=30, seats_taken=0):
        self.course_id = course_id
        self.course_code = course_code
        self.course_name = course_name
        self.department = department
        self.credits = credits
        self.prerequisite_id = prerequisite_id
        self.max_seats = max_seats
        self.seats_taken = seats_taken

    def to_dict(self):
        return {
            "course_id": self.course_id,
            "course_code": self.course_code,
            "course_name": self.course_name,
            "department": self.department,
            "credits": self.credits,
            "prerequisite_id": self.prerequisite_id,
            "max_seats": self.max_seats,
            "seats_taken": self.seats_taken
        }