# services/registration_service.py
from database.db_connect import Database
from models.student import Student
import random
import numpy as np # type: ignore
from sklearn.cluster import KMeans # type: ignore

class RegistrationService:
    def __init__(self):
        self.db = Database()
        self.quizzes = {
            'Intro to Shell and Linux Scripting': [
                {
                    'question': 'What command lists files in a directory?',
                    'options': ['A. dir', 'B. ls', 'C. list', 'D. files'],
                    'answer': 'B'
                },
                {
                    'question': 'Which command changes the current directory?',
                    'options': ['A. cd', 'B. mv', 'C. cp', 'D. rm'],
                    'answer': 'A'
                },
                {
                    'question': 'What does chmod do?',
                    'options': ['A. Change mode', 'B. Copy file', 'C. Move file', 'D. Delete file'],
                    'answer': 'A'
                },
                {
                    'question': 'What is the shebang line?',
                    'options': ['A. #!/bin/bash', 'B. #include', 'C. #define', 'D. #comment'],
                    'answer': 'A'
                },
                {
                    'question': 'What command displays the current user?',
                    'options': ['A. who', 'B. id', 'C. whoami', 'D. user'],
                    'answer': 'C'
                }
            ],
            'Intro to Python and MySQL': [
                {
                    'question': 'How do you connect to MySQL in Python?',
                    'options': ['A. mysql.connect', 'B. mysql-connector-python', 'C. sql.connect', 'D. db.connect'],
                    'answer': 'B'
                },
                {
                    'question': 'What is a Python list comprehension?',
                    'options': ['A. [x for x in range(5)]', 'B. list(range(5))', 'C. {x: x for x in range(5)}', 'D. (x in range(5))'],
                    'answer': 'A'
                },
                {
                    'question': 'What does SELECT * FROM table do?',
                    'options': ['A. Selects one row', 'B. Selects all columns', 'C. Deletes table', 'D. Updates table'],
                    'answer': 'B'
                },
                {
                    'question': 'Which Python type stores key-value pairs?',
                    'options': ['A. List', 'B. Tuple', 'C. Dictionary', 'D. Set'],
                    'answer': 'C'
                },
                {
                    'question': 'What is the Python keyword for defining a function?',
                    'options': ['A. func', 'B. def', 'C. function', 'D. lambda'],
                    'answer': 'B'
                }
            ]
        }

    def add_student(self, first_name, last_name, department, year):
        query = """
        INSERT INTO students (first_name, last_name, department, year)
        VALUES (%s, %s, %s, %s)
        """
        params = (first_name, last_name, department, year)
        self.db.execute_query(query, params)
        return self.db.execute_query("SELECT LAST_INSERT_ID() as student_id", fetch=True)[0]["student_id"]

    def add_course(self, course_name, department):
        query = """
        INSERT INTO courses (course_name, department)
        VALUES (%s, %s)
        """
        params = (course_name, department)
        self.db.execute_query(query, params)
        return self.db.execute_query("SELECT LAST_INSERT_ID() as course_id", fetch=True)[0]["course_id"]

    def add_grade(self, student_id, course_id, grade):
        query = """
        INSERT INTO grades (student_id, course_id, grade)
        VALUES (%s, %s, %s)
        """
        self.db.execute_query(query, (student_id, course_id, grade))

    def take_quiz(self, course_name):
        questions = random.sample(self.quizzes.get(course_name, []), 5)
        correct = 0
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}: {q['question']}")
            for option in q['options']:
                print(option)
            answer = input("Enter your answer (A-D): ").strip().upper()
            if answer == q['answer']:
                correct += 1
        score = (correct / 5) * 100
        return score, correct

    def cluster_students(self, students_data):
        # Prepare data for clustering
        features = []
        for student in students_data:
            shell_grade = float(student['grades'].get('Intro to Shell and Linux Scripting', 0))  # Convert Decimal to float
            python_grade = float(student['grades'].get('Intro to Python and MySQL', 0))  # Convert Decimal to float
            features.append([shell_grade, python_grade])
        
        # Handle case with insufficient data
        if len(features) < 3:
            return ['Needs Support' for _ in students_data]
        
        # Apply K-means clustering
        X = np.array(features)
        kmeans = KMeans(n_clusters=3, random_state=42)
        labels = kmeans.fit_predict(X)
        
        # Map labels to meaningful names (based on average grades)
        cluster_means = [np.mean(X[labels == i], axis=0).mean() for i in range(3)]
        sorted_clusters = np.argsort(cluster_means)
        cluster_names = ['Needs Support', 'Intermediate', 'Advanced']
        label_mapping = {sorted_clusters[i]: cluster_names[i] for i in range(3)}
        
        return [label_mapping[label] for label in labels]

    def view_all_students(self):
        query = """
        SELECT s.student_id, s.first_name, s.last_name, s.department,
               c.course_name, g.grade
        FROM students s
        LEFT JOIN grades g ON s.student_id = g.student_id
        LEFT JOIN courses c ON g.course_id = c.course_id
        """
        results = self.db.execute_query(query, fetch=True)
        students = {}
        for row in results:
            student_id = row['student_id']
            name = f"{row['first_name']} {row['last_name']}".strip()
            if student_id not in students:
                students[student_id] = {
                    'name': name,
                    'department': row['department'],
                    'grades': {}
                }
            if row['course_name']:
                students[student_id]['grades'][row['course_name']] = row['grade']
        
        students_list = list(students.values())
        if students_list:
            clusters = self.cluster_students(students_list)
            for student, cluster in zip(students_list, clusters):
                student['cluster'] = cluster
        return students_list

    def recommend_courses(self, student_id, quiz_results=None):
        query = """
        SELECT c.course_name, g.grade
        FROM grades g
        JOIN courses c ON g.course_id = c.course_id
        WHERE g.student_id = %s
        AND c.course_name IN ('Intro to Shell and Linux Scripting', 'Intro to Python and MySQL')
        """
        grades = self.db.execute_query(query, params=(student_id,), fetch=True)
        
        shell_grade = None
        python_grade = None
        for grade in grades:
            if grade['course_name'] == 'Intro to Shell and Linux Scripting':
                shell_grade = grade['grade']
            if grade['course_name'] == 'Intro to Python and MySQL':
                python_grade = grade['grade']

        if quiz_results is None:
            quiz_results = {}

        adjusted_grades = {}
        if shell_grade is not None:
            adjusted_grades['shell'] = float(shell_grade)  # Convert Decimal to float
        if shell_grade is None and 'Intro to Shell and Linux Scripting' in quiz_results:
            adjusted_grades['shell'] = quiz_results['Intro to Shell and Linux Scripting']['score']
        elif shell_grade is not None and 'Intro to Shell and Linux Scripting' in quiz_results:
            adjusted_grades['shell'] = max(float(shell_grade), quiz_results['Intro to Shell and Linux Scripting']['score'])
        else:
            adjusted_grades['shell'] = float(shell_grade) if shell_grade is not None else 0
        if python_grade is not None:
            adjusted_grades['python'] = float(python_grade)  # Convert Decimal to float
        if python_grade is None and 'Intro to Python and MySQL' in quiz_results:
            adjusted_grades['python'] = quiz_results['Intro to Python and MySQL']['score']
        elif python_grade is not None and 'Intro to Python and MySQL' in quiz_results:
            adjusted_grades['python'] = max(float(python_grade), quiz_results['Intro to Python and MySQL']['score'])
        else:
            adjusted_grades['python'] = float(python_grade) if python_grade is not None else 0

        if adjusted_grades['shell'] >= 70 and adjusted_grades['python'] >= 70:
            return ['Object-Oriented Programming', 'Intro to Web Infra']
        else:
            return ['Intro to Shell and Linux Scripting', 'Object-Oriented Programming', 'Data Structures and Algorithms']

    def get_course_resources(self, course_name):
        resources = {
            'Intro to Shell and Linux Scripting': [
                {'type': 'W3Schools', 'title': 'Linux Tutorial', 'link': 'https://www.w3schools.com/linux/'},
                {'type': 'YouTube', 'title': 'Linux Shell Scripting Tutorial', 'link': 'https://www.youtube.com/watch?v=_n5_2HrV3Zw'},
                {'type': 'Book', 'title': 'Linux Command Line and Shell Scripting Bible', 'link': 'https://www.amazon.com/Linux-Command-Shell-Scripting-Bible/dp/111898384X'}
            ],
            'Intro to Python and MySQL': [
                {'type': 'W3Schools', 'title': 'Python MySQL Tutorial', 'link': 'https://www.w3schools.com/python/python_mysql_getstarted.asp'},
                {'type': 'YouTube', 'title': 'Python MySQL Tutorial for Beginners', 'link': 'https://www.youtube.com/watch?v=3vsC1l19kYI'},
                {'type': 'Book', 'title': 'Python Programming for Beginners', 'link': 'https://www.amazon.com/Python-Programming-Beginners-Introduction-Applications/dp/1731030835'}
            ],
            'Object-Oriented Programming': [
                {'type': 'W3Schools', 'title': 'Python OOP Tutorial', 'link': 'https://www.w3schools.com/python/python_classes.asp'},
                {'type': 'YouTube', 'title': 'OOP in Python', 'link': 'https://www.youtube.com/watch?v=Ej_02ICOIgs'},
                {'type': 'Book', 'title': 'Head First Design Patterns', 'link': 'https://www.amazon.com/Head-First-Design-Patterns-Brain-Friendly/dp/0596007124'}
            ],
            'Intro to Web Infra': [
                {'type': 'W3Schools', 'title': 'Web Development Tutorial', 'link': 'https://www.w3schools.com/html/'},
                {'type': 'YouTube', 'title': 'Web Infrastructure Fundamentals', 'link': 'https://www.youtube.com/watch?v=3RiHcgCrqbI'},
                {'type': 'Book', 'title': 'Web Scalability for Startup Engineers', 'link': 'https://www.amazon.com/Web-Scalability-Startup-Engineers-Artur/dp/0071842837'}
            ],
            'Data Structures and Algorithms': [
                {'type': 'W3Schools', 'title': 'Python Data Structures', 'link': 'https://www.w3schools.com/python/python_lists.asp'},
                {'type': 'YouTube', 'title': 'Data Structures and Algorithms in Python', 'link': 'https://www.youtube.com/watch?v=pkYVOmU3MgA'},
                {'type': 'Book', 'title': 'Introduction to Algorithms', 'link': 'https://www.amazon.com/Introduction-Algorithms-3rd-MIT-Press/dp/0262033844'}
            ]
        }
        return resources.get(course_name, [])

    def close(self):
        self.db.close()