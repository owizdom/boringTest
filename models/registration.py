# models/registration.py
class Registration:
    def __init__(self, registration_id, student_id, course_id, registration_date=None):
        self.registration_id = registration_id
        self.student_id = student_id
        self.course_id = course_id
        self.registration_date = registration_date

    def to_dict(self):
        return {
            "registration_id": self.registration_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "registration_date": self.registration_date
        }