"""
graph_gen.py
This module contains functions to generate various types of graphs using Matplotlib.
"""

import matplotlib.pyplot as plt
import numpy as np
import csv

def extract_info(filename):
    """
    Inputs: 
        filename (str): The name of the file containing the data.
    Outputs:
        num_agents[]: List of number of agents.
        runtime[]: List of runtimes.
    Description:
        This function reads the data from the specified .csv file and extracts the runtime and number of agents
            to plot the data in a graph.
    """
    num_agents = []
    runtime = []
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            num_agents.append(int(row['num_agents']))
            runtime.append(float(row['runtime']))
    
    return num_agents, runtime

def plot_graph(x, y):
    """
    Inputs:
        x[]: List of x values (number of agents).
        y[]: List of y values (runtime).
    Outputs:
        None
    Description:
        This function generates a graph using the provided x and y values.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', marker='o')
    plt.title('Runtime vs Number of Agents')
    plt.xlabel('Number of Agents')
    plt.ylabel('Runtime (s)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('runtime_vs_agents.png')    

if __name__ == "__main__":
    num_agents = []
    runtime = []
    filename = 'runtests.csv'
    num_agents, runtime = extract_info(filename)
    # print(num_agents)
    # print(runtime)
    plot_graph(num_agents, runtime)
    print("Graph generated and saved as runtime_vs_agents.png")