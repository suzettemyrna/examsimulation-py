# Reading txt-files and storing data from them

from exam_simulation.models.question import Question
from exam_simulation.models.examiner import Examiner
from exam_simulation.models.student import Student


def read_questions():
    try:
        questions_file = "../data/questions.txt"
        with open(questions_file, "r") as file:
            questions = []
            for line in file:
                q = Question(line)
                questions.append(q)
        return questions
    except FileNotFoundError:
        raise FileNotFoundError(f"Can't find file '{questions_file}'")
    

def read_students():
    return read_persons("../data/students.txt", Student)


def read_examiners():
    return read_persons("../data/examiners.txt", Examiner)


def read_persons(file, class_func):
    try:
        with open(file, "r") as f:
            persons = []
            for line in f:
                p = class_func(line)
                persons.append(p)
            
        return persons

    except FileNotFoundError:
        raise FileNotFoundError(f"Can't find file '{file}'")