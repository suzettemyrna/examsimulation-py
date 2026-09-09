from exam_simulation.services.simulation import Simulation


def main():
    sim = Simulation()

    try:
        sim.load_data()
        sim.run()

    except Exception as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()