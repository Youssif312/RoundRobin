import time
import sys
import itertools
import threading


def get_positive_int(prompt):
    while True:
        try:
            val = int(input(prompt))
            if val <= 0:
                print("Please enter a positive integer.")
            else:
                return val
        except ValueError:
            print("Invalid input. Enter an integer.")


def get_non_negative_int(prompt):
    while True:
        try:
            val = int(input(prompt))
            if val < 0:
                print("Please enter a non-negative integer.")
            else:
                return val
        except ValueError:
            print("Invalid input. Enter an integer.")


def get_yes_no(prompt):
    while True:
        val = input(prompt).strip().lower()
        if val in ('y', 'n'):
            return val                 
        print("Invalid input. Enter 'y' or 'n'.")


def get_input():
    num = get_positive_int("Enter number of processes: ")
    quantum = get_positive_int("Enter quantum time: ")

    same_arrival = get_yes_no("Do all processes arrive at time 0? (y/n): ")

    processes = []
    for i in range(num):
        burst = get_positive_int(f"Enter burst time for P{i+1}: ")

        if same_arrival == 'y':
            arrival = 0
        else:
            arrival = get_non_negative_int(f"Enter arrival time for P{i+1}: ")

        processes.append([i+1, arrival, burst, burst, None, 0, 0, 0, 0])

    return num, quantum, processes


def quantum_animation():
    animation = ["[■□□□□□□□□□]","[■■□□□□□□□□]", "[■■■□□□□□□□]",
                 "[■■■■□□□□□□]", "[■■■■■□□□□□]", "[■■■■■■□□□□]",
                 "[■■■■■■■□□□]", "[■■■■■■■■□□]",
                 "[■■■■■■■■■□]", "[■■■■■■■■■■]"]

    print("\nChecking quantum vs burst time:")
    for frame in animation:
        time.sleep(0.15)
        sys.stdout.write("\r" + frame)
        sys.stdout.flush()
    print("\n")


def loading_spinner():
    done = False

    def spin():
        for c in itertools.cycle("|/-\\"):
            if done:
                break
            sys.stdout.write("\rLoading " + c)
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\rDone!     \n")

    t = threading.Thread(target=spin)
    t.start()
    time.sleep(2)
    done = True
    t.join()


def get_scheduling_type(processes, quantum):
    max_burst = max(p[2] for p in processes)
    return "FCFS" if quantum >= max_burst else "Round Robin"


def fcfs_scheduling(processes):
    time_counter = 0
    gantt = []

    processes.sort(key=lambda x: x[1])

    for p in processes:
        if time_counter < p[1]:
            gantt.append(("IDLE", time_counter, p[1]))
            time_counter = p[1]

        p[4] = time_counter
        p[8] = p[4] - p[1]
        time_counter += p[2]
        p[5] = time_counter
        p[7] = p[5] - p[1]
        p[6] = p[7] - p[2]

        gantt.append((p[0], p[4], p[5]))

    return gantt


def round_robin_scheduling(processes, quantum, n):
    time_counter = 0
    completed = 0
    gantt = []

    processes.sort(key=lambda x: x[1])

    while completed < n:
        executed = False

        for p in processes:
            if p[3] > 0 and p[1] <= time_counter:
                executed = True

                if p[4] is None:
                    p[4] = time_counter
                    p[8] = p[4] - p[1]

                exec_time = min(quantum, p[3])
                start = time_counter
                time_counter += exec_time
                p[3] -= exec_time

                gantt.append((p[0], start, time_counter))

                if p[3] == 0:
                    p[5] = time_counter
                    p[7] = p[5] - p[1]
                    p[6] = p[7] - p[2]
                    completed += 1

        if not executed:
            next_arrival = min(p[1] for p in processes if p[3] > 0)
            gantt.append(("IDLE", time_counter, next_arrival))
            time_counter = next_arrival

    return gantt


def count_context_switches(gantt):
    if not gantt:
        return 0

    context_switches = 0
    prev_pid = gantt[0][0]

    for pid, _, _ in gantt[1:]:
        if pid != prev_pid:
            context_switches += 1
        prev_pid = pid

    return context_switches


def print_results(processes, gantt, num):
    print("\nPID | AT | BT | WT | TAT | RT")
    wt = tat = rt = 0

    for p in processes:
        wt += p[6]
        tat += p[7]
        rt += p[8]
        print(f"P{p[0]:<2} | {p[1]:<2} | {p[2]:<2} | {p[6]:<2} | {p[7]:<3} | {p[8]:<2}")

    print("\nAverage Waiting Time =", wt / num)
    print("Average Turnaround Time =", tat / num)
    print("Average Response Time =", rt / num)

    cs = count_context_switches(gantt)
    print("Total Context Switches =", cs)

    print("\nGantt Chart:\n")

    scale = 3

    for pid, start, end in gantt:
        print("+" + "-" * ((end - start) * scale), end="")
    print("+")

    for pid, start, end in gantt:
        label = "IDLE" if pid == "IDLE" else f"P{pid}"
        width = (end - start) * scale
        print("|" + label.center(width), end="")
    print("|")

    for pid, start, end in gantt:
        print("+" + "-" * ((end - start) * scale), end="")
    print("+")

    print(gantt[0][1], end="")
    for pid, start, end in gantt:
        spaces = (end - start) * scale
        print(" " * (spaces - len(str(end)) + 1) + str(end), end="")
    print()


def main():
    num, quantum, processes = get_input()

    quantum_animation()

    scheduling_type = get_scheduling_type(processes, quantum)
    print(f"\nExecuting as {scheduling_type} Scheduling...")

    loading_spinner()

    if scheduling_type == "FCFS":
        gantt = fcfs_scheduling(processes)
    else:
        gantt = round_robin_scheduling(processes, quantum, num)

    print_results(processes, gantt, num)


main()