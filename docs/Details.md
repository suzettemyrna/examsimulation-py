# Architecture and Implementation Details

This document describes implementation details and design decisions that are not covered in the main README.

## 1. Concurrency Model

The simulation uses Python threads to represent concurrent examiners.

Each examiner has a dedicated worker thread. All examiner threads operate on the same thread-safe student queue and independently process students as they become available.

The application also uses a separate thread for terminal display. The main thread is responsible for starting the simulation and waiting for its completion.

Conceptually, the application can be represented as:

```text
                    ┌─────────────────┐
                    │   Main Thread   │
                    │  Orchestration  │
                    └────────┬────────┘
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
      ┌────────────┐  ┌────────────┐  ┌────────────┐
      │ Examiner 1 │  │ Examiner 2 │  │ Examiner N │
      │   Thread   │  │   Thread   │  │   Thread   │
      └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                   ┌────────────────┐
                   │  Student Queue │
                   └────────────────┘

                   ┌────────────────┐
                   │ Display Thread │
                   └────────────────┘
````

The workload is primarily simulation and waiting rather than CPU-intensive computation, so threads provide a straightforward way to model simultaneous examiners while keeping shared state accessible.

## 2. Shared Student Queue

Students are stored in a `queue.Queue`, which provides thread-safe access from multiple examiner workers.

An examiner follows this general lifecycle:

1. Wait for a student in the queue.
2. Retrieve the next student.
3. Run the examination.
4. Update the student's state and statistics.
5. Mark the queue task as completed.
6. Continue processing students while work remains.

The main thread uses `Queue.join()` to wait until all queued students have been processed.

This allows the simulation to coordinate an arbitrary number of examiner workers without manually assigning students to individual examiners.

## 3. Student State

Students move through several states during the simulation:

```text
QUEUE → ANSWERING → PASSED
                 ↘ FAILED
```

`QUEUE` indicates that the student is waiting for an examiner.

`ANSWERING` indicates that an examiner is currently conducting the examination.

After the examination, the student receives either `PASSED` or `FAILED`.

The state is used by the display layer to show the current progress of the simulation.

## 4. Examiner State

Each examiner keeps track of information required both for the simulation and for the final statistics.

Important values include:

* current student;
* total number of students examined;
* number of failed students;
* accumulated working time;
* start time of the current examination;
* number of lunch breaks taken.

The examiner therefore acts as both a domain object and a source of statistics about their own work.

## 5. Exam Duration

The duration of an examination depends on the examiner's name length.

For an examiner with a name of length `N`, the duration is randomly selected from:

```text
N - 1 ... N + 1 seconds
```

The generated value is a floating-point number, so examinations do not necessarily last an integer number of seconds.

Two different timing concepts are tracked:

* **student completion time** — how long the student spent waiting and taking the exam;
* **examiner working time** — the amount of active examination time accumulated by the examiner.

These values serve different purposes in the final statistics.

## 6. Examiner Breaks

Examiners become eligible for a lunch break after reaching a working-time threshold.

The threshold is calculated from the number of breaks already taken:

```text
30 × (number_of_previous_breaks + 1)
```

This produces thresholds of approximately:

```text
30 seconds
60 seconds
90 seconds
120 seconds
...
```

The break is checked only after an examination has finished. An examiner therefore never interrupts an active examination.

The break duration is randomly selected between 12 and 18 seconds.

If the simulation continues long enough, the same examiner can take multiple breaks.

An examiner does not start a break when there are no remaining students to process.

## 7. Student Answer Selection

Each question consists of several words from which the student selects one answer.

The selection probability follows a golden-ratio-based distribution.

Let:

```text
φ ≈ 1.618
```

The algorithm starts with a weight and repeatedly divides it by `φ`, producing decreasing weights for subsequent positions.

For example, the relative weights have the form:

```text
1
1 / φ
1 / φ²
1 / φ³
...
```

The resulting weights are normalized and used for weighted random selection.

For female students, the resulting distribution is reversed, giving higher probability to words near the end of the list.

The implementation therefore produces a deliberately non-uniform answer distribution rather than selecting words uniformly at random.

## 8. Examiner Answer Selection

The examiner independently determines which words are considered correct.

The examiner first selects one word from the question and removes it from the pool of available words.

After each selection, there is a one-in-three probability of continuing to select another word.

The process stops when:

* the examiner decides not to continue; or
* all available words have been selected.

This allows a question to have one or several correct answers.

The student's selected word is then compared with the examiner's selected set.

## 9. Question Selection

Three questions are selected for every examination.

Questions are selected without replacement within a single exam. Once a question has been selected, it is removed from the temporary pool used for that exam.

The original question bank remains available for subsequent students.

The simulation also tracks how questions perform across examinations, allowing the final summary to identify the questions associated with the strongest results.

## 10. Examiner Mood

Before the result is determined, an examiner receives one of three mood states.

The intended probabilities are:

| Mood    | Probability | Result             |
| ------- | ----------: | ------------------ |
| Bad     |         1/8 | Automatic failure  |
| Good    |         1/4 | Automatic pass     |
| Neutral |         5/8 | Depends on answers |

For a neutral examiner, the student passes when the number of correct answers is greater than the number of incorrect answers.

With three questions, this means at least two correct answers are required.

The mood is generated independently for each examination.

## 11. Final Statistics

After all students have completed their examinations, the simulation generates a final summary.

The summary includes:

* fastest students among those who passed;
* fastest students among those who failed;
* examiner with the lowest failure rate;
* best-performing questions;
* overall pass rate.

The overall result is considered positive when more than 85% of students pass.

These statistics are calculated from the final state of the student and examiner objects rather than from a separate database or external storage layer.

## 12. Terminal Display

The display system runs independently from the examiner workers.

It periodically refreshes the terminal and shows:

* student states;
* examiner states;
* the number of students remaining in the queue;
* elapsed simulation time.

The terminal is refreshed approximately once per second.

ANSI escape sequences are used to move the cursor and clear the previous output, allowing the simulation to appear as a continuously updating interface rather than a sequence of separate terminal screens.

The display thread terminates once all students have reached a final state.

## 13. Input Data

The simulation reads its input from three plain-text files:

```text
data/
├── examiners.txt
├── students.txt
└── questions.txt
```

The files are intentionally kept separate from the program logic.

This makes it possible to run the same simulation with different sets of students, examiners, and questions without modifying the Python source code.

Users can replace the provided data with their own input as long as the expected file format is preserved.

## 14. Separation of Responsibilities

The source code is divided into several logical layers.

### Models

The `models` package contains the main domain objects:

* `Person`
* `Student`
* `Examiner`
* `Question`
* enumerations describing states and other fixed values.

These classes represent the data and behavior of the simulation domain.

### Services

The `services` package contains the main application logic:

* examination rules;
* simulation orchestration;
* final statistics.

This keeps the core simulation behavior separate from input and presentation.

### Utilities

The `utils` package contains supporting functionality such as:

* reading input files;
* terminal rendering.

The display and file-processing code therefore do not need to contain examination rules.

## 15. Randomness

Several parts of the simulation intentionally use randomized behavior:

* exam duration;
* student answer selection;
* examiner answer selection;
* examiner mood;
* lunch-break duration.

As a result, two executions with the same input data can produce different outcomes and execution times.

This is an intentional property of the simulation rather than an attempt to reproduce deterministic examination results.

## 16. Why Threads?

The original assignment described examiners as separate processes. The current implementation uses threads instead.

This design keeps the shared student queue and domain objects straightforward to manage while still representing simultaneous examiner activity.

The simulated workload is dominated by waiting and state changes rather than CPU-intensive computation, so using threads is sufficient for the intended behavior.

A multiprocessing implementation could be introduced if process isolation became an explicit requirement. In that case, shared state and communication would require additional inter-process coordination.

## 17. Structural Typing as a Possible Extension

The current implementation relies on Python's dynamic typing and does not require explicit interfaces between domain components.

Some parts of the application already depend primarily on an object's behavior rather than its concrete class. This could be made more explicit by introducing structural typing with `typing.Protocol`.

For example, a future interface could describe an object that provides the behavior required by a piece of examination logic without requiring inheritance from a particular base class.

This would make the intended contracts between components clearer while preserving Python's flexible object model.

Structural typing is therefore considered a possible extension rather than a requirement of the current implementation.

## 18. Design Trade-offs

The project deliberately favors a relatively small number of focused components over a more complex architecture.

The main flow can be summarized as:

```text
Input
  ↓
Domain Models
  ↓
Exam Logic
  ↓
Simulation Orchestration
  ↓
Real-Time Display
  ↓
Final Summary
```

This separation keeps the simulation logic independent from the terminal interface and input format while avoiding unnecessary infrastructure for a self-contained simulation.

The architecture is intentionally small enough to remain understandable while still demonstrating concurrency, state management, object-oriented design, probabilistic behavior, and separation of responsibilities.