# main.py
from services.registration_service import RegistrationService
from fpdf import FPDF # type: ignore
import os
import time
import sys
import random

def print_main_menu():
    print("\n=== SmartReg - Course Registration System ===")
    print("SmartReg is a student course enrollment system designed to help")
    print("Software Engineering students manage their 3rd trimester courses")
    print("and receive tailored recommendations for the next trimester.")
    print("\nMain Menu:")
    print("1. Register and Input Grades")
    print("2. View All Students")
    print("3. Exit")

def ai_animation():
    print("\nAI Processing Results...")
    symbols = ['█', '▒', '▐', '▌', '▓']
    for _ in range(20):
        progress = ''.join(random.choice(symbols) for _ in range(30))
        sys.stdout.write(f"\r[{progress}]")
        sys.stdout.flush()
        time.sleep(0.1)
    print("\r" + " " * 40 + "\r", end="")
    print("Processing Complete!")

def generate_pdf(student_name, department, grades, quiz_results, recommendations, resources):
    # Create Student Reports directory if it doesn't exist
    reports_dir = "Student Reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "SmartReg Course Report", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Student Information", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Name: {student_name}", ln=True)
    pdf.cell(200, 10, f"Department: {department}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Grades (Last Trimester)", ln=True)
    pdf.set_font("Arial", size=12)
    if grades:
        for course, grade in grades.items():
            pdf.cell(200, 10, f"{course}: {grade}", ln=True)
    else:
        pdf.cell(200, 10, "No grades entered.", ln=True)
    pdf.ln(10)
    
    if quiz_results:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Quiz Results", ln=True)
        pdf.set_font("Arial", size=12)
        for course, result in quiz_results.items():
            pdf.cell(200, 10, f"{course}: {result['correct']}/5 correct (Score: {result['score']})", ln=True)
        pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Course Recommendations for Next Trimester", ln=True)
    pdf.set_font("Arial", size=12)
    if recommendations:
        for course in recommendations:
            pdf.cell(200, 10, f"- {course}", ln=True)
            if course in resources:
                pdf.cell(200, 10, "  Recommended Resources:", ln=True)
                for resource in resources[course]:
                    pdf.cell(200, 10, f"    - {resource['type']}: {resource['title']} ({resource['link']})", ln=True)
    else:
        pdf.cell(200, 10, "No recommendations available.", ln=True)
    
    pdf_file = os.path.join(reports_dir, f"{student_name.replace(' ', '_')}_report.pdf")
    pdf.output(pdf_file)
    return pdf_file

def main():
    service = RegistrationService()
    while True:
        print_main_menu()
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice == "3":
            print("Exiting SmartReg. Goodbye!")
            service.close()
            break
        elif choice == "2":
            try:
                students = service.view_all_students()
                if students:
                    print("\n=== All Students in Database ===")
                    for student in students:
                        print(f"\nName: {student['name']}")
                        print(f"Department: {student['department']}")
                        print(f"Performance Cluster: {student['cluster']}")
                        print("Grades:")
                        if student['grades']:
                            for course, grade in student['grades'].items():
                                print(f"  {course}: {grade}")
                        else:
                            print("  No grades recorded.")
                else:
                    print("\nNo students found in the database.")
            except Exception as e:
                print(f"Error retrieving student data: {e}")
            continue
        elif choice != "1":
            print("Invalid choice. Please select 1, 2, or 3.")
            continue

        print("\n=== Student Registration ===")
        name = input("Enter your name: ").strip()
        if not name:
            print("Error: Name cannot be empty.")
            continue
        department = "Software Engineering"

        try:
            student_id = service.add_student(name, "", department, 1)
            print(f"Student {name} added with ID: {student_id}")
        except Exception as e:
            print(f"Error adding student: {e}")
            continue

    

        grades = {}
        print("\nAvailable courses:")
        print("1. Intro to Shell and Linux Scripting")
        print("2. Intro to Python and MySQL")
        while True:
            course_choice = input("Select a course to enter grade (1-2, or press Enter to finish): ").strip()
            if course_choice == "":
                break
            if course_choice not in ['1', '2']:
                print("Error: Please select 1 or 2.")
                continue
            course_name = {
                '1': 'Intro to Shell and Linux Scripting',
                '2': 'Intro to Python and MySQL'
            }[course_choice]
            try:
                grade = float(input(f"Enter your grade for {course_name} (0-100): "))
                if not 0 <= grade <= 100:
                    print("Error: Grade must be between 0 and 100.")
                    continue
                course_id = service.add_course(course_name, department)
                service.add_grade(student_id, course_id, grade)
                grades[course_name] = grade
            except ValueError:
                print("Error: Grade must be a number.")
                continue
            except Exception as e:
                print(f"Error adding course/grade: {e}")
                continue

        quiz_results = {}
        failed_courses = [course for course, grade in grades.items() if grade < 70]
        if failed_courses:
            print("\nYou need to improve in the following course(s). Please take the quiz:")
            for course in failed_courses:
                print(f"\nQuiz for {course}:")
                quiz_score, correct = service.take_quiz(course)
                quiz_results[course] = {'score': quiz_score, 'correct': correct}
                print(f"Quiz completed for {course}: {correct}/5 correct (Score: {quiz_score})")
            ai_animation()

        try:
            recommendations = service.recommend_courses(student_id, quiz_results)
            resources = {course: service.get_course_resources(course) for course in recommendations}
            
            export_choice = input("\nWould you like to export your data to a PDF? (yes/no): ").lower()
            if export_choice == 'yes':
                pdf_file = generate_pdf(name, department, grades, quiz_results, recommendations, resources)
                print(f"Data exported to {pdf_file}")
        except Exception as e:
            print(f"Error generating recommendations: {e}")

        continue_choice = input("\nWould you like to return to the main menu? (yes/no): ").lower()
        if continue_choice != 'yes':
            print("Exiting SmartReg. Goodbye!")
            service.close()
            break

    service.close()

if __name__ == "__main__":
    main()