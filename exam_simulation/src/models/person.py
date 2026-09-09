import random

class Person:
    def choose_answer(self, question_words):
        phi = 1.618
        remaining_variety = 1.0
        probs = []
        for _ in range(len(question_words) - 1):
            p = remaining_variety / phi
            probs.append(p)
            remaining_variety -= p
        probs.append(remaining_variety)

        if self.gender.upper == "F":
            probs.reverse()

        return random.choices(question_words, weights=probs)[0]
