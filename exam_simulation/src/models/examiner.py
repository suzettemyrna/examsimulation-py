import random
import time
from models.person import Person
from models.enums import ExaminerMood


class Examiner(Person):
    def __init__(self, name_and_gender):
        self.name, self.gender = name_and_gender.split()

        self.work_time = 0
        self.current_start_time = None

        self.current_student = None
        self.total_students = 0
        self.failed_students = 0

        self.lunch_breaks = 0


    def choose_correct_answers(self, question_words):
        remaining_words = question_words.copy()
        correct_answers = []

        while remaining_words:
            answer = self.choose_answer(remaining_words)
            remaining_words.remove(answer)
            correct_answers.append(answer)

            if random.random() > 1/3: break

        return correct_answers
    

    def go_to_lunch_break(self):
        self.lunch_breaks += 1
        return random.uniform(12, 18)    
    

    @property
    def time_for_one_student(self):
        return random.uniform(len(self.name) - 1, len(self.name) + 1)
    

    @property
    def mood(self):
        roll = random.random()

        if roll < 1 / 8:
            mood = ExaminerMood.BAD
        elif roll < 3 / 8:
            mood = ExaminerMood.GOOD
        else:
            mood = ExaminerMood.NEUTRAL

        return mood

    @property
    def time_for_lunch(self):
        if self.work_time >= 30 * (self.lunch_breaks + 1):
            return True
        return False
    

    @property
    def current_work_time(self):
        if self.current_start_time is None:
            return self.work_time
        return self.work_time + (time.time() - self.current_start_time)


    @property
    def failed_students_percentage(self):
        if self.total_students == 0:
            return 0
        return round(self.failed_students / self.total_students * 100, 2)