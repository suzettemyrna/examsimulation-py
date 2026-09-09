# Displaying info on the screen

from models.enums import StudentStatus


def display_while_exam(students, examiners, elapsed_time):
    print_students_table(students)
    print_examiners_table(examiners)
    print_summary(students, elapsed_time)


def display_after_exam(final_summary):
    print_students_table(final_summary.students)
    print_examiners_table_final(final_summary.examiners)
    print_summary_final(final_summary)


def print_students_table(students):
    print("\033[H\033[J", end="")
    
    headers = ["Student", "Status"]

    students_sorted = sorted(
        students,
        key=lambda s: s.status.value
    )

    rows = [(s.name, s.status) for s in students_sorted]

    print_table(headers, rows)


def print_examiners_table(examiners):
    headers = [
        "Examiner",
        "Current student",
        "Total student",
        "Failed",
        "Work time"
    ]

    rows = []

    for e in examiners:
        current = e.current_student.name if e.current_student else "-"
        rows.append((
            e.name,
            current,
            str(e.total_students),
            str(e.failed_students),
            f"{e.current_work_time:.2f}"
        ))

    print_table(headers, rows)


def print_examiners_table_final(examiners):
    headers = [
        "Examiner",
        "Total students",
        "Failed",
        "Work time"
    ]

    rows = []

    for e in examiners:
        rows.append((
            e.name,
            str(e.total_students),
            str(e.failed_students),
            f"{e.work_time:.2f}"
        ))

    print_table(headers, rows)


def print_summary_final(summary):
    print(f"\nTime from exam start to finish: {summary.elapsed_time:.2f}")
    print("Top-performing students: " + ", ".join(summary.best_students))
    print("Top examiners: " + ", ".join(summary.best_examiners))
    print("Students to be expelled: " + ", ".join(summary.expelled_students))
    print("Best questions: " + ", ".join(summary.best_questions))
    print(f"Result: {"Exam was successful" if summary.result  else "Exam failed"}")


def print_summary(students, elapsed_time):
    queue_count = sum(1 for s in students if s.status == StudentStatus.QUEU)

    print(f"\nRemaining in queue: {queue_count} out of {len(students)}")
    print(f"Time since exam started: {elapsed_time:.2f}")


def print_table(headers, rows):
    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))


    def print_separator():
        print("+" + "+".join("-" * (w + 2) for w in col_widths) + "+")

    
    def print_row(row):
        print(
            "|"
            + "|".join(f" {str(cell).ljust(col_widths[i])} " for i, cell in enumerate(row))
            + "|"
        )


    print_separator()
    print_row(headers)
    print_separator()

    for row in rows:
        print_row(row)

    print_separator()