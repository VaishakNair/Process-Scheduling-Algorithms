from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from queue import Queue
from time import strftime
from time import gmtime

import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly


class Process:
    """Class representing a process."""

    def __init__(self, processName, arrivalTime, burstTime):
        self.processName = processName
        self.arrivalTime = arrivalTime
        self.burstTime = burstTime


readyQueue = Queue()
fcfsDoneList = []

readyList = []
sjfDoneList = []


def populatereadyqueue():
    """Add processes to ready queue (for FCFS)."""
    readyQueue.put(Process("P1", time(0, 0, 1), time(0, 0, 4)))
    readyQueue.put(Process("P2", time(0, 0, 2), time(0, 0, 6)))
    readyQueue.put(Process("P3", time(0, 0, 3), time(0, 0, 2)))


def populatereadylist():
    """Add processes to ready list (for SJF)."""
    readyList.append(Process("P1", time(0, 0, 1), time(0, 0, 4)))
    readyList.append(Process("P2", time(0, 0, 2), time(0, 0, 6)))
    readyList.append(Process("P3", time(0, 0, 3), time(0, 0, 2)))


def scheduleusingfcfs():
    """Schedule processes on a first come, first served basis."""
    df = []
    nextProcessStart = 0
    currentDate = date.today()
    while not readyQueue.empty():
        process = readyQueue.get()
        if nextProcessStart == 0:
            nextProcessStart = process.arrivalTime
        process.completionTime = addTimes(nextProcessStart, process.burstTime)
        fcfsDoneList.append(process)

        df.append(dict(Task=process.processName, Start=str(currentDate) + " " + str(nextProcessStart),
                       Finish=str(currentDate) + " "
                              + str(process.completionTime)))

        print(df[0]['Start'], " Finish: ", df[0]['Finish'])

        nextProcessStart = addTimes(nextProcessStart, process.burstTime)

    fig = ff.create_gantt(df, title="First Come, First Served")
    fig.write_image("./fcfs.png")

    # Calculate turnaround time waiting time
    calculateTurnaroundAndWaitingTime(fcfsDoneList)

    drawTable(fcfsDoneList)


def scheduleusingsjf():
    """Schedule processes based on their burst times with the shortest burst time getting the highest priority."""
    df = []
    currentDate = date.today()

    currentTime = time()  # Time initialized to zero
    completionTime = time()  # Completion time initialized to zero.
    while True:

        # List of processes in the ready queue whose arrival time is less
        # than or equal to the current time
        arrivedProcesses = [x for x in readyList if x.arrivalTime <= currentTime]

        if arrivedProcesses:  # At least one process has arrived
            if currentTime >= completionTime:  # No process is currently undergoing execution
                # Find the shortest job from the list of arrived processes:
                shortestJob = arrivedProcesses[0]
                min = shortestJob.burstTime

                for x in arrivedProcesses:
                    if x.burstTime < min:
                        shortestJob = x
                        min = x.burstTime

                readyList.remove(shortestJob)  # Remove the selected job from ready list:

                # Update the completion time for the job taken up for execution
                shortestJob.completionTime = addTimes(currentTime, shortestJob.burstTime)
                sjfDoneList.append(shortestJob)
                completionTime = shortestJob.completionTime

                # Add the start and end times of the currently executing process to Gantt chart:
                df.append(dict(Task=shortestJob.processName, Start=str(currentDate) + " " + str(currentTime),
                               Finish=str(currentDate) + " "
                                      + str(shortestJob.completionTime)))

        currentTime = addTimes(currentTime, time(second=1))  # Increment current time by 1 second

        if not readyList:  # Ready list is empty. Break out from infinite loop
            break

    fig = ff.create_gantt(df, title="Shortest Job First")
    # plotly.offline.plot(fig, filename='file.html')
    fig.write_image("./sjf.png")

    calculateTurnaroundAndWaitingTime(sjfDoneList)
    drawTable(sjfDoneList)


def drawTable(processList):
    avgTurnaroundTime = getAverageTurnaroundTime(processList)
    avgWaitingTime = getAverageWaitingTime(processList)
    fig = go.Figure(data=[go.Table(header=dict(values=['PID', 'Arrival Time', 'Burst Time',
                                                       'Completion Time', 'Turnaround Time', 'Waiting Time']),
                                   cells=dict(values=[[x.processName for x in processList] + ['<b>Average</b>'],
                                                      [x.arrivalTime for x in processList],
                                                      [x.burstTime for x in processList],
                                                      [x.completionTime for x in processList],
                                                      [x.turnaroundTime for x in processList] + [str(avgTurnaroundTime) + " secs"],
                                                      [x.waitingTime for x in processList] + [str(avgWaitingTime) + " secs"]]))
                          ])
    fig.show()


def getAverageTurnaroundTime(processList):
    times = [timedelta(hours=x.turnaroundTime.hour, minutes=x.turnaroundTime.minute, seconds=x.turnaroundTime.second)
             for x in processList]
    return (sum(times, timedelta()) / len(times)).total_seconds()

def getAverageWaitingTime(processList):
    times = [timedelta(hours=x.waitingTime.hour, minutes=x.waitingTime.minute, seconds=x.waitingTime.second)
             for x in processList]
    return (sum(times, timedelta()) / len(times)).total_seconds()

def calculateTurnaroundAndWaitingTime(processList):
    for process in processList:
        process.turnaroundTime = subtractTimes(process.completionTime, process.arrivalTime)
        process.waitingTime = subtractTimes(process.turnaroundTime, process.burstTime)


def subtractTimes(time1, time2):
    """Subtract second time object from the first and return a time object representing the difference."""
    t1 = timedelta(hours=time1.hour, minutes=time1.minute, seconds=time1.second)
    t2 = timedelta(hours=time2.hour, minutes=time2.minute, seconds=time2.second)
    t3 = t1 - t2
    return (datetime.min + t3).time()


def addTimes(time1, time2):
    """Add two time objects and return a time object representing the sum."""
    t1 = timedelta(hours=time1.hour, minutes=time1.minute, seconds=time1.second)
    t2 = timedelta(hours=time2.hour, minutes=time2.minute, seconds=time2.second)
    t3 = t1 + t2
    return (datetime.min + t3).time()


if __name__ == "__main__":
    populatereadyqueue()
    scheduleusingfcfs()

    populatereadylist()
    scheduleusingsjf()
