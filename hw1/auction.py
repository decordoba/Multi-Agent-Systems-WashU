#!/usr/bin/env

from basic import *  # Find basic.py in https://github.com/decordoba/basic-python
import math
import subprocess

def computeAuctionAlgorithm(matrix, print_results=False):
    """
    From a matrix of nxn elements, in which every row i is the value that agent i gives to n
    objects, we will find the stable matching that links each agent an object, so that we
    maximize the overall value received by all agent from their assigned objects.
    Example:
             OBJECTS    RESULT:  Agent  Object
              2 4 0                1      1
      AGENTS  1 5 0                2      2
              1 3 2                3      3
    """
    s = {}
    t = {}
    numAgents = len(matrix)
    numObjects = len(matrix[0])
    priceObjects = [0] * numObjects
    epsilon = 0.75 / numAgents  # Epsilon must be < 1/n
    agent = 0
    while len(s) < numAgents:
        # Skip all the agents that already have an object assigned
        if agent in s:
            agent = (agent + 1) % numAgents
            continue
        # Calculate the utility of each object according to the agent's value and their price
        utilityObjects = [valueObject - priceObjects[i] for i, valueObject in enumerate(matrix[agent])]
        # Find the first and second object with the highest utility according to agent
        max_val1, max_idx1 = getMaxAndIndex(utilityObjects)
        utilityObjects[max_idx1] = MIN_INT
        max_val2 = max(utilityObjects)
        # Update the price of the chosen object max_idx1
        priceObjects[max_idx1] += max_val1 - max_val2 + epsilon
        # Remove agent which had chosen the max_idx1 object
        if max_idx1 in t:
            del s[t[max_idx1]]
        # Set our agent to the max_idx1 object
        s[agent] = max_idx1
        t[max_idx1] = agent
        # Increase agent counter
        agent = (agent + 1) % numAgents

    # Print results
    if print_results:
        agents = [[ag + 1, s[ag] + 1, matrix[ag][s[ag]], priceObjects[s[ag]]] for ag in s]
        printNicer([["Agent", "Object", "Value", "Price"]] + agents)

    # Calculate value of objects for agents that received them
    valueObjects = [matrix[ag][s[ag]] for ag in s]
    return valueObjects

def generateRandomAssignment(n, M):
    """
    Generate random matrix of n x n, where each cell is assigned uniformly a value from 0 ot M-1
    """
    return [[random.randint(0, M-1) for i in xrange(n)] for i in xrange(n)]

def repeatExperiment(n, M, num_runs, max_n=None, max_M=None, step_n=2, step_M=2, LP=True):
    """
    Perform auction algorithm with a random assignemnt and print the average stats
    The assignment will be with n objects/agents, each taking a random value from
    0 to M-1 and each experiment wil be repeated num_runs times. Also, n and M will
    be incremented in steps of step_n / step_M each iteration, and will stop when
    max_n / max_M is reached
    """
    mean_values = []
    mean_times = []
    start_time = getTime()
    prev_time = start_time
    M0 = M
    if max_n is None:
        max_n = n
        step_n = 2
    if max_M is None:
        max_M = M
        step_M = 2
    n_vect = []
    while n <= max_n:
        n_vect.append(n)
        M = M0
        M_vect = []
        while M <= max_M:
            M_vect.append(M)
            meanCost = 0
            meanTime = 0
            for i in range(num_runs):
                data = generateRandomAssignment(n, M)
                time0 = getTime()
                if LP:
                    meanCost += mean(runLPFile("auction.mod", n, data))
                else:
                    meanCost += mean(computeAuctionAlgorithm(data))
                meanTime += getTime() - time0
                if (i * 10) % num_runs == 0:
                    print "{}% -".format(100 * i / num_runs),
            print "{}% - Elapsed time: {}s".format(100, getTime() - prev_time)
            prev_time = getTime()
            mean_values.append(float(meanCost) / num_runs)
            mean_times.append(meanTime / num_runs)
            print "n = {:3}, M = 1e{:1}, Average time: {}s, Average value: {}".format(n, int(math.log10(M)), mean_times[-1], mean_values[-1])
            M *= step_M
        n *= step_n
    print "Total elapsed time: {}".format(getTime() - start_time)
    print "Mean values:", mean_values
    print "Mean times:", mean_times
    return (mean_values, mean_times, n_vect, M_vect)

def createAuctionDatFile(filename, num_obj, num_ag, c):
    """
    Creates a file styled as a .dat file (the kind that GLPK can understand) with params n, m and c,
    where n and m are integers and c is an nxm matrix of integers
    """
    try:
        with open(filename, "w+") as f:
            f.write("data;\n")
            f.write("param n := {};\n".format(num_obj))
            f.write("param m := {};\n".format(num_ag))
            f.write("param c :{} :=\n".format(returnTableRowRight(8, range(1, num_obj + 1))))
            semicolon = ""
            for i, row in enumerate(c):
                if i == num_ag - 1: semicolon = " ;"
                f.write("     {}{}\n".format(returnTableRowRight(8, i+1, row), semicolon))
            f.write("end;\n")

    except IOError:
        print "Error while creating file [{}]".format(filename)
        return False
    return True

def runLPFile(filename, n, c, print_results=False):
    """
    Create tmp.dat from n and c, and run glpsol -m filename -d tmp.dat, which allows us to run the
    GLPK file filename with the input that we saved in tmp.dat. The results returned from GLPK will
    be returned
    """
    # These are my paths hardcoded (It's dirty, I know). Add yours to try the code in your machine
    glpsol = 'C:/Users/Daniel/Downloads/winglpk-4.61/glpk-4.61/w64/glpsol.exe'
    filepath = 'C:/Users/Daniel/DANIEL/Washinton University/Multi-Agent Systems/hw1/'
    datname = "tmp.dat"
    executable = filepath + filename
    datpath = filepath + datname

    # Create tmp.dat file with the data for the Liner Program
    createAuctionDatFile(datpath, num_obj=n, num_ag=n, c=c)
    # Run Linear Program filename and save answer
    answer = subprocess.check_output([glpsol, "-m", executable, "-d", datpath])

    # Parse the answer and return only the part that we care about (the table)
    # This expects an answer like the one that auction.mod would return. If it is not, table
    # will not make any sense
    record_answer = False
    record_values = False
    table = ""
    object_values = []
    for line in answer.split("\n"):
        if line.startswith("Agent") and "Object" in line and "Value" in line:
            record_answer = True
        if "----" in line:
            record_values = False
        if record_answer:
            table += line + "\n"
        if record_values:
            object_values.append(parseString(line, "int")[0][-1])
        if line.startswith("Agent") and "Object" in line and "Value" in line:
            record_values = True
        if "  Total:  " in line:
            record_answer = False

    # Print results if prompted
    if print_results:
        print table
    # Return mean values
    return object_values


if __name__ == "__main__":
    default = """89 42 0 2 24 20 40 37 30 77
                 66 75 9 59 69 66 52 14 85 36
                 82 68 0 81 36 25 48 53 11 68
                 6 96 82 53 17 70 26 12 91 82
                 34 86 22 18 66 73 82 88 18 36
                 90 43 43 93 80 96 12 28 74 93
                 19 75 30 48 31 76 84 29 20 15
                 29 73 88 9 36 40 40 19 1 45
                 77 31 6 68 36 40 22 43 27 61
                 70 21 2 89 30 91 66 74 79 92"""

    """ EXERCISE 1.a
    Solve the default input. Every row is an agent and the numbers in the row are the values
    it gives to every objects. The goal is to find the matching of agents and objects.
    We will solve this through Linear Programming (you need GLPK) and through Python
    """
    # Compute default, or file passed as an argument
    input = readFileArgument(default, print_input=True)
    printSeparator()
    data = parseString(input)
    convertListToInt(data)
    print "INPUT"
    printNicer(data)
    printSeparator()
    print "RESULT USING PYTHON"
    computeAuctionAlgorithm(data, print_results=True)
    printSeparator()
    print "RESULT USING LINEAR PROGRAMING (GLPK)"
    runLPFile("auction.mod", len(data), data, print_results=True)
    printSeparator("X")

    """ EXERCISE 1.b
    Now repeat the above experiment but with random nxn matrices of objects ranging from 0 to 99.
    Plot the average value assigned to each chose object for all n values
    """
    # Results obtained (the experiment takes several hours to complete)
    print "EXPERIMENT NOT USING LINEAR PROGRAMMING, n=2:*2:256, M=100, num_runs=1000"
    n1 = [2, 4, 8, 16, 32, 64, 128, 256]
    # n = 2:*2:256, M = 100, num_runs = 1000
    (mean1, t1, n1, M1) = repeatExperiment(n=2, M=100, num_runs=1000, max_n=256, step_n=2, LP=False)
    # Plot results
    plt.figure(1)
    plotLine(mean1, n1, y_label="Mean Object Value", x_label="n", x_scale="log", show=False,
             color="b", style="-x")
    printSeparator("X")

    """ EXERCISE 1.c
    Finally repeat the previous experiment but this time maintaining n=256, and trying different
    values of M (the range of the values that the objects can take).
    Plot the mean time taken to solve the problem when solving them through LP and through Python
    """
    # Results obtained (the experiment takes several hours to complete)
    print "EXPERIMENT USING LINEAR PROGRAMMING, n=256, M=1e1:*10:1e7, num_runs=100"
    # n = 256, M = 1e1:*10:1e7, num_runs = 100
    (mean2, t2, n2, M2) = repeatExperiment(n=256, M=10, num_runs=100, max_M=10000000, step_M=10,
                                           LP=True)
    printSeparator()
    print "EXPERIMENT NOT USING LINEAR PROGRAMMING, n=256, M=1e1:*10:1e7, num_runs=100"
    (mean3, t3, n3, M3) = repeatExperiment(n=256, M=10, num_runs=100, max_M=10000000, step_M=10,
                                           LP=False)
    # Plot results
    plt.figure(2)
    plotLine(t2, M2, y_label="Mean Time Taken (LP)", x_label="M", x_scale="log", show=False,
             color="b", style="-x")
    plt.figure(3)
    plotLine(t3, M3, y_label="Mean Time Taken (Python)", x_label="M", x_scale="log", show=False,
             color="b", style="-x")
    plt.show()
