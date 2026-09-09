# Exam logic

import random
from models.enums import StudentStatus, ExaminerMood


def exam_for_one_student(examiner, student, questions):
    remaining_questions = questions.copy()
    questions_count = 3
    correct_answers = 0
    for _ in range(questions_count):
        question = examiner_chooses_question(remaining_questions)

        examiners_answers = examiner.choose_correct_answers(question.words)

        students_answer = student.choose_answer(question.words)

        if students_answer in examiners_answers:
            correct_answers += 1
            i = questions.index(question)
            questions[i].answered += 1

    student.status = has_student_passed_exam(examiner, correct_answers)

    return student.status


def examiner_chooses_question(remaining_questions):
    question = random.choice(remaining_questions)
    remaining_questions.remove(question)
    return question


def has_student_passed_exam(examiner, correct_answers):
    examiners_mood = examiner.mood

    if examiners_mood == ExaminerMood.BAD:
        return StudentStatus.FAILED
    elif examiners_mood == ExaminerMood.GOOD:
        return StudentStatus.PASSED
    else:
        if correct_answers >= 2:
            return StudentStatus.PASSED
        else:
            return StudentStatus.FAILED