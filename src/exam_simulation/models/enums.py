from enum import Enum


class ExaminerMood(Enum):
    NEUTRAL = 0
    GOOD = 1
    BAD = 2


class StudentStatus(Enum):
    QUEUE = 0
    ANSWERING = 1
    PASSED = 2
    FAILED = 3

    def __str__(self):
        if self in (StudentStatus.QUEUE, StudentStatus.ANSWERING):
            return "In queue"
        elif self == StudentStatus.PASSED:
            return "Passed"
        elif self == StudentStatus.FAILED:
            return "Failed"