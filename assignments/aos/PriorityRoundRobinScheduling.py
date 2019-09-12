"""Implements Priority and Round Robin scheduling algorithms.

@author Vaishak K Nair 19MCMI08 (MTech AI)
"""

from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from queue import Queue

import plotly.figure_factory as ff
import plotly.graph_objects as go


class Process:
    """Class representing a process."""

    def __init__(self, processName, priority, arrivalTime, burstTime):
        self.processName = processName
        self.priority = priority
        self.arrivalTime = arrivalTime
        self.burstTime = burstTime
        self.remainingBurstTime = burstTime

    def priorityval(self):
        return self.priority

    def __repr__(self):
        return self.processName


priorityReadyList = []
priorityDoneList = []

readyList = []
roundRobinDoneList = []


def populatepriorityreadylist():
    """Add processes to ready list (for priority scheduling)."""
    priorityReadyList.append(Process("P1", 1, time(0, 0, 1), time(0, 0, 4)))
    priorityReadyList.append(Process("P2", 3, time(0, 0, 2), time(0, 0, 6)))
    priorityReadyList.append(Process("P3", 2, time(0, 0, 2), time(0, 0, 2)))



def populatereadylist():
    """Add processes to ready list (for Round Robin scheduling)."""
    readyList.append(Process("P1", 0, time(0, 0, 1), time(0, 0, 4)))
    readyList.append(Process("P2", 0, time(0, 0, 2), time(0, 0, 6)))
    readyList.append(Process("P3", 0, time(0, 0, 3), time(0, 0, 2)))


def scheduleusingpriority():
    """Schedule processes based on their priorities, 1 being the highest priority."""

    df = [] # List to hold data needed to draw Gantt chart.
    nextProcessStart = 0
    currentDate = date.today()
    priorityReadyList.sort(key=Process.priorityval)
    print(priorityReadyList)
    while priorityReadyList:
        process = priorityReadyList.pop(0)
        if nextProcessStart == 0:
            nextProcessStart = process.arrivalTime
        process.completionTime = addTimes(nextProcessStart, process.burstTime)
        priorityDoneList.append(process)

        df.append(dict(Task=process.processName, Start=str(currentDate) + " " + str(nextProcessStart),
                       Finish=str(currentDate) + " "
                              + str(process.completionTime)))

        nextProcessStart = addTimes(nextProcessStart, process.burstTime)

    fig = ff.create_gantt(df, title="Priority")
    fig.write_image("./priority.png")

    calculateTurnaroundAndWaitingTime(priorityDoneList)
    drawPriorityTable(priorityDoneList, "priorityTable.png")


def scheduleusingroundrobin():
    """Schedule processes using Round Robin scheduling policy."""
    df = []  # List to hold data needed to draw Gantt chart.
    round_robin_time_slice = 3
    roundRobinQueue = Queue()
    currentDate = date.today()

    currentTime = time()  # Time initialized to zero
    currentProcess = None
    while True:

        # List of processes in the ready queue whose arrival time is less
        # than or equal to the current time
        arrivedProcesses = [x for x in readyList if x.arrivalTime <= currentTime]
        # Add the newly arrived processes, if any, to round robin queue:
        for process in arrivedProcesses:
            roundRobinQueue.put(process)
            readyList.remove(process)  # Remove the process from ready list

        if currentProcess and currentProcess.remainingBurstTime > time():
            roundRobinQueue.put(currentProcess)
        elif currentProcess:
            roundRobinDoneList.append(currentProcess)
            currentProcess.completionTime = currentTime
            currentProcess = None

        if not roundRobinQueue.empty():
            currentProcess = roundRobinQueue.get()
        if currentProcess:
            startTime = currentTime
            for i in range(1, round_robin_time_slice + 1):
                # Update the remaining burst time of the process under execution:
                currentProcess.remainingBurstTime = subtractTimes(currentProcess.remainingBurstTime, time(second=1))
                currentTime = addTimes(currentTime, time(second=1))  # Increment current time by 1 second.
                if currentProcess.remainingBurstTime == time():  # Process has completed execution
                    break


            # Add the start and end times of the currently executing process to Gantt chart:
            df.append(dict(Task=currentProcess.processName, Start=str(currentDate) + " " + str(startTime),
                               Finish=str(currentDate) + " "
                                    + str(currentTime), Resource=currentProcess.processName))
        else:
            currentTime = addTimes(currentTime, time(second=1))  # Increment current time by 1 second.

        if not readyList \
                and roundRobinQueue.empty()\
                and currentProcess.remainingBurstTime == time():
            # Ready list and round robin queue are empty and all processes have finished execution:
            currentProcess.completionTime = currentTime
            roundRobinDoneList.append(currentProcess)
            break  # Break out from infinite loop

    colors = {'P1': 'rgb(220, 0, 0)',
              'P2': 'rgb(119, 25, 230)',
              'P3': 'rgb(0, 255, 100)'}
    fig = ff.create_gantt(df, title="Round Robin (Time slice: 3 secs)", group_tasks=True,
                          colors=colors,
                          index_col='Resource')
    fig.write_image("./round_robin.png")

    calculateTurnaroundAndWaitingTime(roundRobinDoneList)
    drawTable(roundRobinDoneList, "roundRobinTable.png")


def drawPriorityTable(processList, fileName):
    avgTurnaroundTime = getAverageTurnaroundTime(processList)
    avgWaitingTime = getAverageWaitingTime(processList)
    fig = go.Figure(data=[go.Table(header=dict(values=['PID', 'Priority', 'Arrival Time', 'Burst Time',
                                                       'Completion Time', 'Turnaround Time', 'Waiting Time']),
                                   cells=dict(values=[[x.processName for x in processList] + ['<b>Average</b>'],
                                                      [x.priority for x in processList],
                                                      [x.arrivalTime for x in processList],
                                                      [x.burstTime for x in processList],
                                                      [x.completionTime for x in processList],
                                                      [x.turnaroundTime for x in processList] + [str(avgTurnaroundTime) + " secs"],
                                                      [x.waitingTime for x in processList] + [str(avgWaitingTime) + " secs"]]))
                          ])
    fig.write_image("./" + fileName)

def drawTable(processList, fileName):
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
    fig.write_image("./" + fileName)


def getAverageTurnaroundTime(processList):
    """Compute average of turnaround times of the passed in processes."""
    times = [timedelta(hours=x.turnaroundTime.hour, minutes=x.turnaroundTime.minute, seconds=x.turnaroundTime.second)
             for x in processList]
    return (sum(times, timedelta()) / len(times)).total_seconds()

def getAverageWaitingTime(processList):
    """Compute average of waiting times of the passed in processes."""
    times = [timedelta(hours=x.waitingTime.hour, minutes=x.waitingTime.minute, seconds=x.waitingTime.second)
             for x in processList]
    return (sum(times, timedelta()) / len(times)).total_seconds()

def calculateTurnaroundAndWaitingTime(processList):
    """Calculate turnaround time and waiting time."""
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
    populatepriorityreadylist()
    scheduleusingpriority()

    populatereadylist()
    scheduleusingroundrobin()
