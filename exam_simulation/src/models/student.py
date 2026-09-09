from models.person import Person
from models.enums import StudentStatus


class Student(Person):
    def __init__(self, name_and_gender):
        self.name, self.gender = name_and_gender.split()
        self.status = StudentStatus.QUEUE
        self.time = 0