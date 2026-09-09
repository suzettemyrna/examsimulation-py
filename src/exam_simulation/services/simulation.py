# Orchestrator

import time
import threading
from queue import Queue

from exam_simulation.models.enums import StudentStatus
from exam_simulation.utils.io import read_questions, read_students, read_examiners
from exam_simulation.utils.display import display_while_exam, display_after_exam
from exam_simulation.services.exam_logic import exam_for_one_student
from exam_simulation.services.final_summary import Summary


class Simulation:
    def __init__(self):
        self.questions = []
        self.students = []
        self.examiners = []

        self.start_time = None
        self.elapsed_time = 0

        self.students_queue = Queue()


    def load_data(self):
        self.questions = read_questions()
        if self.questions == Exception: return Exception

        self.examiners = read_examiners()
        if self.examiners == Exception: return Exception

        self.students = read_students()
        if self.students == Exception: return Exception
        for s in self.students:
            self.students_queue.put(s)


    def run(self):
        self.start_time = time.time()

        threads = []

        display_thread = threading.Thread(target=self.display_loop)
        display_thread.start()

        for examiner in self.examiners:
            t = threading.Thread(target=self.examiner_worker, args=(examiner,))
            t.start()
            threads.append(t)

        self.students_queue.join()
        display_thread.join()

        final_summary = Summary(self.students, self.examiners, self.questions, self.elapsed_time)
        display_after_exam(final_summary)


    def display_loop(self):
        while True:
            self.elapsed_time = time.time() - self.start_time
            display_while_exam(self.students, self.examiners, self.elapsed_time)

            if all(s.status in (StudentStatus.PASSED, StudentStatus.FAILED) for s in self.students):
                break

            time.sleep(1)


    def examiner_worker(self, examiner):
        while not self.students_queue.empty():
            student = self.students_queue.get()

            self.run_one_examiner(examiner, student)

            self.students_queue.task_done()


    def run_one_examiner(self, examiner, student):
        start = time.time()
        self.student_comes_in(examiner, student)

        time.sleep(examiner.time_for_one_student)

        mark = exam_for_one_student(examiner, student, self.questions)
        self.student_comes_out(examiner, student, mark)

        student.time = time.time() - start

        if examiner.time_for_lunch:
            if self.students_queue.empty():
                return
            lunch_time = examiner.go_to_lunch_break()
            time.sleep(lunch_time)


    def student_comes_in(self, examiner, student):
        student.status = StudentStatus.ANSWERING

        examiner.current_start_time = time.time()
        examiner.current_student = student
        examiner.total_students += 1


    def student_comes_out(self, examiner, student, mark):
        student.status = mark

        examiner.work_time += time.time() - examiner.current_start_time
        examiner.current_start_time = None        
        examiner.current_student = None
        if mark == StudentStatus.FAILED:
            examiner.failed_students += 1