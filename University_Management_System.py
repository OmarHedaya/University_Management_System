from abc import ABC, abstractmethod
from multipledispatch import dispatch
import Library_DB
import time

class Person(ABC):
    def __init__(self, person_name, person_id, contact_info):
        self.person_name = person_name
        self.person_id = person_id
        self.contact_info = contact_info

    @abstractmethod
    def get_info(self):
        pass

    def update_contact(self, new_contact):
        self.contact_info = new_contact
        print(f"{self.person_name}'s contact info updated.")

class Student(Person):
    def __init__(self, student_id, student_name, major, contact_info):
        super().__init__(student_name, student_id, contact_info)
        self.major = major
        self.courses_enrolled = []
        self.grades = {}

    def enroll_course(self, course):
        if course not in self.courses_enrolled:
            print(f"{self.person_name} enrolled in {course.name}")
            course.add_student(self)
            self.courses_enrolled.append(course)
        else:
            print(f"{self.person_name} is already enrolled in {course.name}")

    def drop_course(self, course):
        if course in self.courses_enrolled:
            self.courses_enrolled.remove(course)
            print(f"{self.person_name} dropped {course.name}")
            course.remove_student(self)

    def view_grades(self):
        print(f"\nGrades for {self.person_name}:")
        for course, grade in self.grades.items():
            print(f"{course.name}: {grade}")
        return self.grades

    def calculate_gpa(self):
        total_courses = len(self.grades)
        if total_courses == 0:
            print(f"{self.person_name} has no grades yet.")
            return 0.0
        grade_map = {
            "A+": 4.0, "A": 3.9, "A-": 3.7,
            "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7,
            "D+": 1.3, "D": 1.0, "D-": 0.7,
            "F": 0.0
        }
        total_points = sum(grade_map.get(grade.upper(), 0.0) for grade in self.grades.values())
        gpa = total_points / total_courses
        print(f"{self.person_name}'s GPA is {gpa:.2f}")
        return gpa

    def get_info(self):
        return {
            'ID': self.person_id,
            'Name': self.person_name,
            'Major': self.major,
            'Email': self.contact_info,
            'Courses': [course.name for course in self.courses_enrolled],
            'Grades': {course.name: grade for course, grade in self.grades.items()}
        }

class Professor(Person):
    def __init__(self, professor_id, name, department, contact_info):
        super().__init__(name, professor_id, contact_info)
        self.department = department
        self.courses_taught = []

    def assign_grade(self, student, course, grade):
        if course in self.courses_taught and course in student.courses_enrolled:
            student.grades[course] = grade
            print(f"{self.person_name} assigned grade {grade} to {student.person_name} in {course.name}")

    def view_students(self, course):
        if course in self.courses_taught:
            return [student.person_name for student in course.enrolled_students]
        return []

    def get_info(self):
        return {
            'ID': self.person_id,
            'Name': self.person_name,
            'Department': self.department,
            'Contact': self.contact_info,
            'Courses': [course.name for course in self.courses_taught]
        }

class Department:
    def __init__(self, department_id, name, head_of_department):
        self.department_id = department_id
        self.name = name
        self.head_of_department = head_of_department
        self.courses_offered = []
        self.faculty_members = []

    def get_info(self):
        return {
            'Department ID': self.department_id,
            'Name': self.name,
            'Head of Department': self.head_of_department,
            'Courses Offered': [course.name for course in self.courses_offered],
            'Faculty Members': [professor.person_name for professor in self.faculty_members]
        }

    def list_courses(self):
        for course in self.courses_offered:
            print(course.name)

    def list_professors(self):
        for professor in self.faculty_members:
            print(professor.person_name)

class Schedule:
    def __init__(self, day, time_, semester, year):
        self.day = day
        self.time = time_
        self.semester = semester
        self.year = year

    def update_schedule(self, day, time_, semester, year):
        self.day = day
        self.time = time_
        self.semester = semester
        self.year = year

    def view_schedule(self):
        print(f"Schedule: {self.day} at {self.time}, Semester: {self.semester}, Year: {self.year}")

class Course:
    def __init__(self, course_id, name, department, credit_hours, professor):
        self.course_id = course_id
        self.name = name
        self.department = department
        self.credit_hours = credit_hours
        self.professor = professor
        self.enrolled_students = []
        self.schedule = None

    @dispatch(Professor)
    def assign_professor(self, professor):
        self.professor = professor
        if self not in professor.courses_taught:
            professor.courses_taught.append(self)
        print(f"{professor.person_name} has been assigned to {self.name}")

    @dispatch(Student)
    def add_student(self, student):
        if student not in self.enrolled_students:
            self.enrolled_students.append(student)
            print(f"{student.person_name} has been enrolled in {self.name}")

    @dispatch(Student)
    def remove_student(self, student):
        if student in self.enrolled_students:
            self.enrolled_students.remove(student)
            if self in student.courses_enrolled:
                student.courses_enrolled.remove(self)
            print(f"{student.person_name} has been removed from {self.name}")

    def get_course_info(self):
        return {
            'Course ID': self.course_id,
            'Name': self.name,
            'Department': self.department.name if isinstance(self.department, Department) else str(self.department),
            'Credit Hours': self.credit_hours,
            'Professor': self.professor.person_name if self.professor else None,
            'Enrolled Students': [student.person_name for student in self.enrolled_students]
        }

    @dispatch(Schedule)
    def assign_schedule(self, schedule):
        self.schedule = schedule
        print(f"Schedule assigned to {self.name}: {schedule.day} at {schedule.time}, Semester: {schedule.semester}, Year: {schedule.year}")

class Classroom:
    def __init__(self, room_number, capacity, location, availability=True):
        self.room_number = room_number
        self.capacity = capacity
        self.location = location
        self.availability = availability
        self.schedule = None

    @dispatch(Course, Schedule)
    def assign_classroom(self, course, schedule):
        print(f"Classroom {self.room_number} assigned to {course.name} on {schedule.day} at {schedule.time}")
        self.availability = False
        self.schedule = schedule

    def check_availability(self):
        if self.availability:
            print(f"Classroom {self.room_number} is available")
        else:
            print(f"Classroom {self.room_number} is already booked")

    def get_classroom_info(self):
        return {
            'Room Number': self.room_number,
            'Capacity': self.capacity,
            'Location': self.location,
            'Availability': self.availability
        }

class Exam:
    def __init__(self, exam_code, course, duration):
        self.exam_code = exam_code
        self.course = course
        self.duration = duration
        self.student_result = []
        self.schedule = None

    @dispatch(int, Course, int, Schedule)
    def schedule_exam(self, exam_code, course, duration, schedule):
        print(f"Exam {exam_code} for {course.name} scheduled on {schedule.day} at {schedule.time} for {duration} hours")
        self.schedule = schedule

    @dispatch(Student, str)
    def record_result(self, student, grade):
        self.student_result.append((student.person_name, grade))
        print(f"Result recorded for {student.person_name}: {grade}")

    def view_results(self):
        print("Exam Results:")
        for student, grade in self.student_result:
            print(f"{student}: {grade}")

    def get_exam_info(self):
        return {
            'Exam Code': self.exam_code,
            'Course': self.course.name,
            'Duration': self.duration,
            'Results': [(student, grade) for student, grade in self.student_result]
        }

class Admin:
    def __init__(self, admin_id, name, contact_info):
        self.admin_id = admin_id
        self.name = name
        self.contact_info = contact_info
        self.students = []
        self.professors = []
        self.courses = []
        self.schedule = []
        self.classrooms = []
        self.exams = []

    def get_info(self):
        return {
            'ID': self.admin_id,
            'Name': self.name,
            'Contact': self.contact_info
        }

    def add_student(self):
        print("Enter student details:")
        student_id = input("Student ID: ")
        student_name = input("Student Name: ")
        major = input("Major: ")
        contact_info = input("Contact Info: ")
        student = Student(student_id, student_name, major, contact_info)
        self.students.append(student)
        print(f"Student {student_name} added successfully.")

    def manage_student(self):
        print("Manage Student:")
        student_id = input("Enter Student ID: ")
        for student in self.students:
            if str(student.student_id) == student_id:
                print(student.get_info())
                action = input("Choose an action (enroll/drop/view grades/assign grade): ").lower()
                if action == "enroll":
                    course_id = input("Enter course ID to enroll: ")
                    for course in self.courses:
                        if str(course.course_id) == course_id:
                            student.enroll_course(course)
                            break
                elif action == "drop":
                    course_id = input("Enter course ID to drop: ")
                    for course in self.courses:
                        if str(course.course_id) == course_id:
                            student.drop_course(course)
                            break
                elif action == "view grades":
                    student.view_grades()
                elif action == "assign grade":
                    course_id = input("Enter course ID to assign grade: ")
                    for course in self.courses:
                        if str(course.course_id) == course_id:
                            grade = input("Enter grade: ")
                            student.grades[course] = grade
                            print(f"Grade {grade} assigned to {student.person_name} in {course.name}")
                            break
                else:
                    print("Invalid action.")
                return
        print("Student not found.")

    def remove_student(self):
        print("Remove Student:")
        student_id = input("Enter Student ID: ")
        for student in self.students:
            if str(student.person_id) == student_id:
                # Remove student from all courses
                for course in self.courses:
                    if student in course.enrolled_students:
                        course.remove_student(student)
                self.students.remove(student)
                print(f"Student {student.person_name} removed successfully.")
                return
        print("Student not found.")

    def print_students(self):
        print("\nAll Students:")
        for student in self.students:
            info = student.get_info()
            print(f"\nID: {info['ID']}")
            print(f"Name: {info['Name']}")
            print(f"Major: {info['Major']}")
            print(f"Email: {info['Email']}")
            print(f"Courses: {info['Courses']}")
            print(f"Grades: {info['Grades']}")

    def print_professors(self):
        print("\nAll Professors:")
        for professor in self.professors:
            info = professor.get_info()
            print(f"\nID: {info['ID']}")
            print(f"Name: {info['Name']}")
            print(f"Department: {info['Department']}")
            print(f"Contact: {info['Contact']}")
            print(f"Courses: {info['Courses']}")

    def print_courses(self):
        print("\nAll Courses:")
        for course in self.courses:
            info = course.getcourse_info()
            print(f"\nID: {info['Course ID']}")
            print(f"Name: {info['Name']}")
            print(f"Department: {info['Department']}")
            print(f"Credit Hours: {info['Credit Hours']}")
            print(f"Professor: {info['Professor']}")
            print(f"Enrolled Students: {info['Enrolled Students']}")

    def add_professor(self):
        print("Enter professor details: ")
        professor_id = input("Professor ID: ")
        name = input("Name: ")
        department = input("Department: ")
        contact_info = input("Contact Info: ")
        professor = Professor(professor_id, name, department, contact_info)
        self.professors.append(professor)
        print(f"Professor {name} added successfully.")

    def manage_professor(self):
        print("Manage Professor:")
        professor_id = input("Enter Professor ID: ")
        for professor in self.professors:
            if str(professor.person_id) == professor_id:
                print(professor.get_info())
                action = input("Choose an action (assign course/view students): ").lower()
                if action == "assign course":
                    course_id = input("Enter course ID to assign: ")
                    for course in self.courses:
                        if str(course.course_id) == course_id:
                            course.assign_professor(professor)
                            break
                elif action == "view students":
                    course_id = input("Enter course ID to view students: ")
                    for course in self.courses:
                        if str(course.course_id) == course_id:
                            students = professor.view_students(course)
                            print(f"Students enrolled in {course.name}: {students}")
                            break
                else:
                    print("Invalid action.")
                return
        print("Professor not found.")

    def remove_professor(self):
        print("Remove Professor:")
        professor_id = input("Enter Professor ID: ")
        for professor in self.professors:
            if str(professor.person_id) == professor_id:
                # Remove professor from all courses
                for course in self.courses:
                    if course.professor == professor:
                        course.professor = None
                self.professors.remove(professor)
                print(f"Professor {professor.person_name} fired successfully.")
                return
        print("Professor not found.")

    def add_course(self):
        print("Enter course details:")
        course_id = input("Course ID: ")
        name = input("Course Name: ")
        department = input("Department: ")
        credit_hours = int(input("Credit Hours: "))
        professor_id = input("Professor ID: ")
        professor = next((p for p in self.professors if str(p.person_id) == professor_id), None)
        if professor:
            course = Course(course_id, name, department, credit_hours, professor)
            self.courses.append(course)
            print(f"Course {name} added successfully.")
        else:
            print("Professor not found.")

    def manage_course(self):
        print("Manage Course:")
        course_id = input("Enter Course ID: ")
        for course in self.courses:
            if str(course.course_id) == course_id:
                print(course.get_course_info())
                action = input("Choose an action (enroll/drop/assign professor): ").lower()
                if action == "enroll":
                    student_id = input("Enter student ID to enroll: ")
                    for student in self.students:
                        if str(student.person_id) == student_id:
                            course.add_student(student)
                            break
                elif action == "drop":
                    student_id = input("Enter student ID to drop: ")
                    for student in self.students:
                        if str(student.person_id) == student_id:
                            course.remove_student(student)
                            break
                elif action == "assign professor":
                    professor_id = input("Enter professor ID to assign: ")
                    for professor in self.professors:
                        if str(professor.person_id) == professor_id:
                            course.assign_professor(professor)
                            break
                else:
                    print("Invalid action.")
                return
        print("Course not found.")

    def remove_course(self):
        print("Remove Course:")
        course_id = input("Enter Course ID: ")
        for course in self.courses:
            if str(course.course_id) == course_id:
                # Remove course from all students' enrolled courses
                for student in self.students:
                    if course in student.courses_enrolled:
                        student.courses_enrolled.remove(course)
                # Remove course from professor's taught courses
                if course.professor:
                    if course in course.professor.courses_taught:
                        course.professor.courses_taught.remove(course)
                self.courses.remove(course)
                print(f"Course {course.name} removed successfully.")
                return
        print("Course not found.")

    def add_schedule(self):
        print("Enter schedule details:")
        day = input("Day: ")
        time_ = input("Time: ")
        semester = input("Semester: ")
        year = int(input("Year: "))
        schedule = Schedule(day, time_, semester, year)
        self.schedule.append(schedule)
        print(f"Schedule added successfully.")

    def assign_schedule_to_course(self):
        print("Assign Schedule to Course:")
        course_id = input("Enter Course ID: ")
        for course in self.courses:
            if course.course_id == course_id:
                day = input("Day: ")
                time_ = input("Time: ")
                semester = input("Semester: ")
                year = int(input("Year: "))
                schedule = Schedule(day, time_, semester, year)
                course.schedule = schedule
                print(f"Schedule assigned to {course.name} successfully.")
                return
        print("Course not found.")

    def assign_schedule_to_classroom(self):
        print("Assign Schedule to Classroom:")
        room_number = input("Enter Classroom Room Number: ")
        for classroom in self.classrooms:
            if classroom.room_number == room_number:
                day = input("Day: ")
                time_ = input("Time: ")
                semester = input("Semester: ")
                year = int(input("Year: "))
                schedule = Schedule(day, time_, semester, year)
                classroom.schedule = schedule
                print(f"Schedule assigned to Classroom {classroom.room_number} successfully.")
                return
        print("Classroom not found.")

    def assign_schedule_to_exam(self):
        print("Assign Schedule to Exam:")
        exam_code = input("Enter Exam Code: ")
        for exam in self.exams:
            if exam.exam_code == exam_code:
                day = input("Day: ")
                time_ = input("Time: ")
                semester = input("Semester: ")
                year = int(input("Year: "))
                schedule = Schedule(day, time_, semester, year)
                exam.schedule = schedule
                print(f"Schedule assigned to Exam {exam.exam_code} successfully.")
                return
        print("Exam not found.")

    def add_classroom(self):
        print("Enter classroom details:")
        room_number = input("Room Number: ")
        capacity = int(input("Capacity: "))
        location = input("Location: ")
        classroom = Classroom(room_number, capacity, location)
        self.classrooms.append(classroom)
        print(f"Classroom {room_number} added successfully.")

    def manage_classroom(self):
        print("Manage Classroom:")
        room_number = input("Enter Classroom Room Number: ")
        for classroom in self.classrooms:
            if classroom.room_number == room_number:
                print(classroom.get_classroom_info())
                action = input("Choose an action (assign/unassign/check availability): ").lower()
                if action == "assign":
                    course_name = input("Enter course name to assign: ")
                    for course in self.courses:
                        if course.name == course_name:
                            schedule = Schedule(course.schedule.day, course.schedule.time, course.schedule.semester, course.schedule.year)
                            classroom.assign_classroom(course, schedule)
                            break
                elif action == "unassign":
                    classroom.availability = True
                    print(f"Classroom {classroom.room_number} unassigned successfully.")
                elif action == "check availability":
                    classroom.check_availability()
                else:
                    print("Invalid action.")
                return
        print("Classroom not found.")

    def add_exam(self):
        print("Enter exam details:")
        exam_code = input("Exam Code: ")
        course_name = input("Course Name: ")
        duration = int(input("Duration (in hours): "))
        for course in self.courses:
            if course.name == course_name:
                exam = Exam(exam_code, course, duration)
                self.exams.append(exam)
                print(f"Exam {exam_code} added successfully.")
                return
        print("Course not found.")

    def manage_exam(self):
        print("Manage Exam:")
        exam_code = input("Enter Exam Code: ")
        for exam in self.exams:
            if exam.exam_code == exam_code:
                print(exam.get_exam_info())
                action = input("Choose an action (record result/view results): ").lower()
                if action == "record result":
                    student_name = input("Enter student name: ")
                    grade = input("Enter grade: ")
                    for student in self.students:
                        if student.person_name == student_name:
                            exam.record_result(student, grade)
                            break
                elif action == "view results":
                    exam.view_results()
                else:
                    print("Invalid action.")
                return
        print("Exam not found.")

    def remove_exam(self):
        print("Remove Exam:")
        exam_code = input("Enter Exam Code: ")
        for exam in self.exams:
            if exam.exam_code == exam_code:
                self.exams.remove(exam)
                print(f"Exam {exam.exam_code} removed successfully.")
                return
        print("Exam not found.")

class Library:
    def __init__(self):
        self.__books = [(book[0],book[1]) for book in Library_DB.get_all_books()]
        self.__library_id = [student[1] for student in Library_DB.get_all_students_id()]
        self.__employee_id = [employee[1] for employee in Library_DB.get_all_employees_id()]

    def update_books(self):
        self.__books = [(book[0],book[1]) for book in Library_DB.get_all_books()]

    def update_library_id(self):
        self.__library_id = [student[1] for student in Library_DB.get_all_students_id()]

    def update_employee_id(self):
        self.__employee_id = [employee[1] for employee in Library_DB.get_all_employees_id()]

    def add_book(self, book_name):
        if not any(book[1] == book_name for book in self.__books):
            Library_DB.add_book(book_name)
            self.update_books()
            print(f"{book_name} book added to library")
        else:
            print("Book already registered")

    def remove_book(self, book_name):
        if any(book[1] == book_name for book in self.__books):
            Library_DB.remove_book(book_name)
            self.update_books()
            print(f"{book_name} book removed from library")
        else:
            print("Book not registered")

    @dispatch(str,str)
    def borrow_book(self, student_id, book_name):
        if any(book[0] == book_name for book in self.__books):
            Library_DB.borrow_book(student_id, book_name)
            self.update_books()
        else:
            print(f"{book_name} book not registered")

    @dispatch(str, int)
    def borrow_book(self, student_id, book_id):
        if any(book[1] == book_id for book in self.__books):
            Library_DB.borrow_book(student_id,book_id)
            self.update_books()
        else:
            print("book not registered")

    def return_book(self, book_name):
        if not any(book[1] == book_name for book in self.__books):
            Library_DB.return_book(book_name)
            self.update_books()
        else:
            print(f"{book_name} book already exists in library")

    def check_availability_books(self, book_name):
        if any(book[0] == book_name for book in self.__books):
            print(f"{book_name} book is available")
        else:
            print(f"{book_name} book is not available")

    def add_library_id(self,student_id):
        if id not in self.__library_id:
            Library_DB.add_student(student_id)
            self.update_library_id()
        else:
            print("ID already registered")

    def remove_library_id(self,student_id):
        try:
            student_id = int(student_id)
            if student_id in self.__library_id:
                Library_DB.remove_student(student_id)
                self.update_library_id()
            else:
                print("ID not registered")
        except ValueError:
            print("Invalid ID format. Please enter a numeric ID.")

    def students_login_id(self, student_id):
        if student_id.lower() == "register":
            while True:
                try:
                    student_id = int(input("Enter your ID: "))
                    if student_id in self.__library_id:
                        print(f"ID {student_id} already registered")
                        return -1
                    else:
                        self.add_library_id(student_id)
                        return -1
                except ValueError:
                    print("Please enter a valid numeric ID!")
        else:
            try:
                if int(student_id) in self.__library_id:
                    print(f"Welcome ID {student_id}!")
                else:
                    print(f"Please register")
                    return -1
            except ValueError:
                print("Invalid ID format. Please enter a numeric ID.")
                return -1

    def employees_login_id(self, student_id):
        try:
            if int(student_id) in self.__employee_id:
                print(f"Welcome ID {student_id}!")
            else:
                print("You are not an employee!")
                return -1
        except ValueError:
            print("Invalid ID format. Please enter a numeric ID.")
            return -1

    @staticmethod
    def finalization():
         while True:
            final = input("Any other services?(Y/N)").lower()
            if final == "y":
                return -2
            elif final == "n":
                print("Thank you for using this service!")
                return -3
            else:
                print("Please enter a valid input!")
                continue


    def services(self, student_id, is_student=True):
        while True:
            if is_student:
                menu = "1) Borrow\n2) Return\n3) Check availability books\n4) Exit\n"
            else:
                menu = "1) Add\n2) Remove\n3) Check availability\n4) Remove Student ID\n5) Exit\n"

            service = input(f"Please choose the number of the service:\n{menu}")
            try:
                if int(service) == 1:

                    if is_student:
                        Library_DB.show_books()
                        book = input("Please enter the name or index of the book:")
                        if book.isdigit():
                            book_id = int(book)
                            self.borrow_book(student_id, book_id)
                        else:
                            book = book.lower()
                            self.borrow_book(student_id, book)
                    else:
                        book=input("Please enter the name of the book:")
                        self.add_book(book)

                elif int(service) == 2:
                    if is_student:
                        book = input("Please enter the name of the book:").lower()
                        self.return_book(book)
                    else:
                        Library_DB.show_books()
                        book = input("Please enter the name or the index of the book:")
                        if book.isdigit():
                            book_id = int(book)
                            self.remove_book(book_id)
                        else:
                            book = book.lower()
                            self.remove_book(book)

                elif int(service) == 3:
                    book = input("Please enter the name of the book:")
                    self.check_availability_books(book)
                elif int(service) == 4:
                    if is_student:
                        print("Thank you for using this service!")
                        return -1
                    else:
                        student_id = input("Please enter the ID of the student to remove:")
                        self.remove_library_id(student_id)

                elif int(service) == 5:
                    print("Thank you for using this service!")
                    return -1
            except ValueError:
                print("Please enter a valid number!")
                continue

            final = self.finalization()
            if final == -2:
                continue
            elif final == -3:
                return -1

    def main(self,person):
        print("Welcome to the library service!")
        time.sleep(2.5)
        while True:
            if person == "student":
                while True:
                    student_id = input("Please enter your ID (type register if you want to register):")
                    if self.students_login_id(student_id) == -1:
                        continue
                    if self.services(student_id, is_student=True) == -1:
                        time.sleep(3)
                        break
                break
            elif person == "admin":
                while True:
                    student_id = input("Please enter your ID: ")
                    if self.employees_login_id(student_id) == -1:
                        continue
                    if self.services(student_id, is_student=False) == -1:
                        time.sleep(3)
                        break
                break
            else:
                print("Please enter a valid input!")
                continue

def interface():
    dept = Department(1, "Computer Science", "Prof. Mostafa Soliman")
    prof1 = Professor(101, "Dr. Mohamed issa", "Computer Science", "Mohamed@univ.edu")
    prof2 = Professor(102, "Dr. Mostafa ElSayed", "Computer Science", "Mostafa@univ.edu")
    prof3= Professor(103, "Dr. Ayman Arafa", "Computer Science", "Ayman@univ.edu")
    prof4= Professor(104, "Dr. Hassan Shokry", "Computer Science", "Hassan@univ.edu")
    student1 = Student(320240098, "Aly Mohamed Aly", "CS", "Aly@univ.edu")
    student2 = Student(320240096, "Omar Ahmed Hedaya", "CS", "Omar@univ.edu")
    student3 = Student(320240103, "Belal Abdallah AbdElLatif", "CS", "Belal@univ.edu")
    student4 = Student(320240099, "Ahmed Abaza", "CS", "Ahmed@univ.edu")
    student5= Student(320240083, "Salma Mohamed","Cs","Salma@univ.edu")
    student6= Student(320240156, "Tarek Mohamed","Cs","Tarek@univ.edu")
    course1 = Course(301, "Advanced Programming", dept, 3, prof1)
    course2 = Course(302, "Data Structures", dept, 3, prof2)
    course3 = Course(303, "Math 2", dept, 3, prof3)
    course4 = Course(304, "Physics 2", dept, 3, prof4)
    

    dept.courses_offered.extend([course1, course2, course3, course4])
    dept.faculty_members.extend([prof1, prof2, prof3, prof4])
    prof1.courses_taught.append(course1)
    prof2.courses_taught.append(course2)
    prof3.courses_taught.append(course3)
    prof4.courses_taught.append(course4)
    course1.enrolled_students.append(student1)
    course2.enrolled_students.append(student1)
    course3.enrolled_students.append(student1)
    course4.enrolled_students.append(student1)
    course1.enrolled_students.append(student2)
    course2.enrolled_students.append(student2)
    course3.enrolled_students.append(student2)
    course4.enrolled_students.append(student2)
    course1.enrolled_students.append(student3)
    course2.enrolled_students.append(student3)
    course3.enrolled_students.append(student3)
    course4.enrolled_students.append(student3)
    course1.enrolled_students.append(student4)
    course2.enrolled_students.append(student4)
    course3.enrolled_students.append(student4)
    course4.enrolled_students.append(student4)
    course1.enrolled_students.append(student5)
    course2.enrolled_students.append(student5)
    course3.enrolled_students.append(student5)
    course4.enrolled_students.append(student5)
    course1.enrolled_students.append(student6)
    course2.enrolled_students.append(student6)
    course3.enrolled_students.append(student6)
    course4.enrolled_students.append(student6)
    student1.courses_enrolled.append(course1)
    student2.courses_enrolled.append(course1)
    student3.courses_enrolled.append(course1)
    student4.courses_enrolled.append(course1)
    student1.courses_enrolled.append(course2)
    student2.courses_enrolled.append(course2)
    student3.courses_enrolled.append(course2)
    student4.courses_enrolled.append(course2)
    student1.courses_enrolled.append(course3)
    student2.courses_enrolled.append(course3)
    student3.courses_enrolled.append(course3)
    student4.courses_enrolled.append(course3)
    student1.courses_enrolled.append(course4)
    student2.courses_enrolled.append(course4)
    student3.courses_enrolled.append(course4)
    student4.courses_enrolled.append(course4)
    student5.courses_enrolled.append(course1)
    student5.courses_enrolled.append(course2)
    student5.courses_enrolled.append(course3)
    student5.courses_enrolled.append(course4)
    student6.courses_enrolled.append(course1)
    student6.courses_enrolled.append(course2)
    student6.courses_enrolled.append(course3)
    student6.courses_enrolled.append(course4)

    students = {str(student1.person_id): student1, str(student2.person_id): student2,str(student3.person_id): student3,str(student4.person_id): student4,str(student5.person_id): student5,str(student6.person_id): student6}
    professors = {str(prof1.person_id): prof1, str(prof2.person_id): prof2,str(prof3.person_id): prof3,str(prof4.person_id): prof4}
    courses = {str(course1.course_id): course1, str(course2.course_id): course2, str(course3.course_id): course3, str(course4.course_id): course4}

    admin1 = Admin(122,"Admin_1","admin_1@univ.edu")
    admin2 = Admin(123,"Admin_2","admin_2@univ.edu")
    admin3 = Admin(124,"Admin_3","admin_3@univ.edu")

    admin3.students = list(students.values())
    admin3.professors = list(professors.values())
    admin3.courses = list(courses.values())

    admin2.students=list(students.values())
    admin2.professors=list(professors.values())
    admin2.courses=list(courses.values())

    admin1.students = list(students.values())
    admin1.professors = list(professors.values())
    admin1.courses = list(courses.values())
    admins={str(admin1.admin_id):admin1,str(admin2.admin_id):admin2,str(admin3.admin_id):admin3}

    print("\n\n\n\nWelcome to the University System!")
    while True:
        print("\nLogin:")
        role = input("Are you a student, professor, or admin? (student/professor/admin, or 'exit' to quit): ").strip().lower()
        if role == 'exit':
            print("Goodbye!")
            time.sleep(3)
            break
        user_id = input("Enter your ID: ").strip()
        if role == 'student' and user_id in students:
            student_menu(students[user_id],dept,role)
        elif role == 'professor' and user_id in professors:
            professor_menu(professors[user_id])
        elif role == 'admin' and user_id in admins:
            admin_menu(admins[user_id])
        else:
            print("Invalid credentials. Try again.") 

def student_menu(student,dept,role):
    while True:
        print(f"\nWelcome, {student.person_name} (Student)")
        print("1. View Info")
        print("2. View Grades")
        print("3. Calculate GPA")
        print("4. Update Contact Info")
        print("5. Enroll in Course")
        print("6. Drop Course")
        print("7. Library Services")
        print("8. Logout")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            info = student.get_info()
            for k, v in info.items():
                print(f"{k}: {v}")

        elif choice == '2':
            student.view_grades()

        elif choice == '3':
            student.calculate_gpa()

        elif choice == '4':
            new_contact = input("Enter new contact info: ")
            student.update_contact(new_contact)

        elif choice == '5':
            course_id = input("Enter course ID to enroll: ").strip()
            course = next((c for c in dept.courses_offered if str(c.course_id) == course_id), None)
            if not course:
                print("Course not found.")
                continue
            student.enroll_course(course)

        elif choice == '6':
            course_id = input("Enter course ID to drop: ").strip()
            course = next((c for c in student.courses_enrolled if str(c.course_id) == course_id), None)
            if not course:
                print("Course not found.")
            else:
                student.drop_course(course)

        elif choice == '7':
            library = Library()
            library.main(role)
            print("Returning to main menu...")
            time.sleep(2.5)

        elif choice == '8':
            print("Logging out...")
            time.sleep(2.5)
            break
        else:
            print("Invalid option.")

def professor_menu(professor):
    while True:
        print(f"\nWelcome, {professor.person_name} (Professor)")
        print("1. View Info")
        print("2. View My Courses")
        print("3. Assign Grade")
        print("4. Update Contact Info")
        print("5. Logout")
        choice = input("Choose an option: ").strip()
        if choice == '1':
            info = professor.get_info()
            for k, v in info.items():
                print(f"{k}: {v}")
        elif choice == '2':
            for course in professor.courses_taught:
                print(f"{course.name} (ID: {course.course_id})")
        elif choice == '3':
            course_id = input("Enter course ID: ").strip()
            course = next((c for c in professor.courses_taught if str(c.course_id) == course_id), None)
            if not course:
                print("You do not teach this course.")
                continue
            print("Enrolled students:")
            for idx, student in enumerate(course.enrolled_students):
                print(f"{idx+1}. {student.person_name} (ID: {student.person_id})")
            stu_id = input("Enter student ID to assign grade: ").strip()
            student = next((s for s in course.enrolled_students if str(s.person_id) == stu_id), None)
            if not student:
                print("Student not found in this course.")
                continue
            grade = input("Enter grade (A, B+, etc.): ").strip().upper()
            if grade not in ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"]:
                print("Invalid grade.")
                continue
            professor.assign_grade(student, course, grade)
        elif choice == '4':
            new_contact = input("Enter new contact info: ")
            professor.update_contact(new_contact)
        elif choice == '5':
            print("Logging out...")
            time.sleep(2.5)
            break
        else:
            print("Invalid option.")
def admin_menu(admin):
    while True:
        print(f"\nWelcome, {admin.name} (Admin)")
        print("1. Manage Students")
        print("2. Manage Professors")
        print("3. Manage Courses")
        print("4. Manage Schedules")
        print("5. Manage Classrooms")
        print("6. Manage Exams")
        print("7. View Info")
        print("8. Library Services")
        print("9. Logout")
        choice = input("Choose an option: ").strip()
        
        if choice == '1':
            print("\nStudent Management:")
            print("1. Add Student")
            print("2. Manage Student")
            print("3. Remove Student")
            print("4. View All Students")
            subchoice = input("Choose an option: ").strip()
            if subchoice == '1':
                admin.add_student()
            elif subchoice == '2':
                admin.manage_student()
            elif subchoice == '3':
                admin.remove_student()
            elif subchoice == '4':
                admin.print_students()
            else:
                print("Invalid option.")
                
        elif choice == '2':
            print("\nProfessor Management:")
            print("1. Add Professor")
            print("2. Manage Professor")
            print("3. Remove Professor")
            print("4. View All Professors")
            subchoice = input("Choose an option: ").strip()
            if subchoice == '1':
                admin.add_professor()
            elif subchoice == '2':
                admin.manage_professor()
            elif subchoice == '3':
                admin.remove_professor()
            elif subchoice == '4':
                admin.print_professors()
            else:
                print("Invalid option.")
                
        elif choice == '3':
            print("\nCourse Management:")
            print("1. Add Course")
            print("2. Manage Course")
            print("3. Remove Course")
            print("4. View All Courses")
            subchoice = input("Choose an option: ").strip()
            if subchoice == '1':
                admin.add_course()
            elif subchoice == '2':
                admin.manage_course()
            elif subchoice == '3':
                admin.remove_course()
            elif subchoice == '4':
                admin.print_courses()
            else:
                print("Invalid option.")
                
        elif choice == '4':
            print("\nSchedule Management:")
            print("1. Add Schedule")
            print("2. Assign Schedule to Course")
            print("3. Assign Schedule to Classroom")
            print("4. Assign Schedule to Exam")
            subchoice = input("Choose an option: ").strip()
            if subchoice == '1':
                admin.add_schedule()
            elif subchoice == '2':
                admin.assign_schedule_to_course()
            elif subchoice == '3':
                admin.assign_schedule_to_classroom()
            elif subchoice == '4':
                admin.assign_schedule_to_exam()
            else:
                print("Invalid option.")
                
        elif choice == '5':
            print("\nClassroom Management:")
            print("1. Add Classroom")
            print("2. Manage Classroom")
            subchoice = input("Choose an option: ").strip()
            if subchoice == '1':
                admin.add_classroom()
            elif subchoice == '2':
                admin.manage_classroom()
            else:
                print("Invalid option.")
                
        elif choice == '6':
            print("\nExam Management:")
            print("1. Add Exam")
            print("2. Manage Exam")
            print("3. Remove Exam")
            subchoice = input("Choose an option: ").strip()
            if subchoice == '1':
                admin.add_exam()
            elif subchoice == '2':
                admin.manage_exam()
            elif subchoice == '3':
                admin.remove_exam()
            else:
                print("Invalid option.")
                
        elif choice == '7':
            info = admin.get_info()
            for k, v in info.items():
                print(f"{k}: {v}")
                
        elif choice == '8':
            library1 = Library()
            library1.main(role)
            print("Returning to main menu...")
            time.sleep(2.5)

        elif choice == '9':
            print("Logging out...")
            time.sleep(2.5)
            break
            
        else:
            print("Invalid option.")



if __name__ == "__main__":
    interface()
                 