import mysql.connector
from mysql.connector import Error

# Download the CA certificate from your Aiven service overview page in the Aiven Console
# (under Connection information > Download CA certificate) and save it as 'ca.pem'
# in the same directory as this script. This enables SSL verification for secure connection.

class Database:
    def __init__(self, host="mysql-3cc1879-gokun4621-314a.f.aivencloud.com", port=19778, user="avnadmin", password="AVNS_0F1Eo6kQc5K4kBQaQMI", database="defaultdb"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.initialize_database()

    def initialize_database(self):
        try:
            # Connect directly to the existing database
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                ssl_ca='ca.pem',
                ssl_verify_cert=True,
                use_pure=True
            )
            cursor = self.connection.cursor()

            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id INT PRIMARY KEY AUTO_INCREMENT,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    department VARCHAR(50) NOT NULL,
                    year INT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    course_id INT PRIMARY KEY AUTO_INCREMENT,
                    course_name VARCHAR(100) NOT NULL,
                    department VARCHAR(50) NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grades (
                    grade_id INT PRIMARY KEY AUTO_INCREMENT,
                    student_id INT NOT NULL,
                    course_id INT NOT NULL,
                    grade DECIMAL(5,2) NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (course_id) REFERENCES courses(course_id)
                )
            """)

            # Pre-populate courses
            cursor.execute("""
                INSERT IGNORE INTO courses (course_name, department) VALUES
                ('Intro to Shell and Linux Scripting', 'Software Engineering'),
                ('Intro to Python and MySQL', 'Software Engineering'),
                ('Intro to Web Infra', 'Software Engineering'),
                ('Basics of Web Development', 'Software Engineering'),
                ('Data Structures and Algorithms', 'Software Engineering'),
                ('Object-Oriented Programming', 'Software Engineering')
            """)
            self.connection.commit()
            cursor.close()
            print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise RuntimeError(f"Failed to connect to MySQL: {e}")

    def execute_query(self, query, params=None, fetch=False):
        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if fetch:
                result = cursor.fetchall()
                return result
            self.connection.commit()
        except Error as e:
            print(f"Error executing query: {e}")
            raise
        finally:
            cursor.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")