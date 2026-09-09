class Question:
    def __init__(self, text):
        self.text = text.strip()
        self.words = text.split()
        self.answered = 0