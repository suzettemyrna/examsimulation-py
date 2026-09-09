# Final screenshot of info and required statistics calculation

from exam_simulation.models.enums import StudentStatus


EPS = 0.01


class Summary:
    def __init__(self, students, examiners, questions, elapsed_time):
        self.students = students
        self.examiners = examiners
        self.questions = questions
        self.elapsed_time = elapsed_time

        self.best_students = self.get_best_students()
        self.best_examiners = self.get_best_examiners()
        self.expelled_students = self.get_expelled_students()
        self.best_questions = self.get_best_questions()
        self.result = self.get_result()


    # students who passed the exam the fastest
    def get_best_students(self):
        return self._get_fastest(StudentStatus.PASSED)


    # students who failed and finished earlier than other students who also failed
    def get_expelled_students(self):
        return self._get_fastest(StudentStatus.FAILED)
    

    def _get_fastest(self, status):
        students = [s for s in self.students if s.status == status]

        if not students:
            return []

        key_func = lambda s: s.time

        min_val = min(key_func(s) for s in students)

        return [
            s.name
            for s in students
            if abs(s.time - min_val) < EPS
        ]


    #  examiners with the lowest failure rate among their students
    def get_best_examiners(self):
        min_val = min(e.failed_students_percentage for e in self.examiners)

        return [
            e.name
            for e in self.examiners
            if e.failed_students_percentage == min_val
        ]


    # questions that were correctly answered by the highest number of students
    def get_best_questions(self):
        answered_questions = [q for q in self.questions if q.answered > 0]

        if answered_questions == []: return []

        max_val = max(q.answered for q in answered_questions)

        return [
            q.text
            for q in answered_questions
            if q.answered == max_val
        ]


    # exam is successful if more than 85% of students pass
    def get_result(self):
        total = len(self.students)
        passed = sum(s.status == StudentStatus.PASSED for s in self.students)

        return total > 0 and (passed / total > 0.85)