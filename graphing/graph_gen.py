"""
graph_gen.py
This module contains functions to generate various types of graphs using Matplotlib.
"""

import matplotlib.pyplot as plt
import numpy as np
import csv

def clean_data(runtests_filepath, memory_results_filepath):
    """
    Inputs: 
        runtests_filepath (str): The path to the cleaned runtests data file.
        memory_results_filepath (str): The path to the memory results data file.
    Outputs:
        None
    Description:
        This function reads the data from the specified .csv file and cleans it by removing any unnecessary
        characters or formatting and rows with -1 in the solution cost column.
    """
    
    # Read the data from the CSV files
    with open(runtests_filepath, 'r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)  # Read the header row
        data = list(csv_reader)  # Read all rows into a list
    
    with open(memory_results_filepath, 'r') as file:
        csv_reader = csv.reader(file)
        memory_headers = next(csv_reader)  # Read the header row
        memory_data = list(csv_reader)  # Read all rows into a list

    # Check which columns have all zeros and filter out rows with -1 solution cost
    all_zero_columns = []
    filtered_data = []
    filtered_memory_data = []
    solution_cost_idx = headers.index("solution cost")
    
    # First, identify all-zero columns
    for col_idx in range(len(headers)):
        all_zeros = True
        for row in data:
            try:
                if col_idx < len(row) and float(row[col_idx]) != 0:
                    all_zeros = False
                    break
            except (ValueError, IndexError):
                all_zeros = False
                break
        if all_zeros:
            all_zero_columns.append(col_idx)

    # Filter out rows with -1 solution cost
    for row_idx in range(len(data)):
        try:
            if data[row_idx][solution_cost_idx] != "-1":
                filtered_data.append(data[row_idx])
                filtered_memory_data.append(memory_data[row_idx])
        except (ValueError, IndexError):
            continue
        

    # Filter out all-zero columns from headers
    cleaned_headers = []
    for idx, header in enumerate(headers):
        if idx not in all_zero_columns:
            cleaned_headers.append(header)
    
    # Remove all-zero columns from data
    cleaned_rows = []  
    for row in filtered_data:
        cleaned_row = []
        for idx, value in enumerate(row):
            if idx not in all_zero_columns:
                cleaned_row.append(value)
        cleaned_rows.append(cleaned_row)

    # Write cleaned data back to a file
    cleaned_filename = runtests_filepath.replace('.csv', '_cleaned.csv')
    with open(cleaned_filename, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(cleaned_headers)
        csv_writer.writerows(cleaned_rows)
    
    # Write cleaned memory data back to a file
    cleaned_memory_filename = memory_results_filepath.replace('.csv', '_cleaned.csv')
    with open(cleaned_memory_filename, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(memory_headers)
        csv_writer.writerows(filtered_memory_data)

def extract_info(runtests_cleaned_filepath, memory_results_filepath):
    """
    Inputs: 
        runtests_cleaned_filepath (str): The path to the cleaned runtests data file.
        memory_results_filepath (str): The path to the memory results data file.
    Outputs:
        num_agents[]: List of number of agents.
        runtime[]: List of runtimes.
        solution_cost[]: List of solution costs.
        ram_usage[]: List of RAM usage.
    Description:
        This function reads the data from the specified .csv file and extracts the runtime and number of agents
            to plot the data in a graph.
    """
    num_agents = []
    runtime = []
    solution_cost = []
    ram_usage = []
    with open(runtests_cleaned_filepath, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            num_agents.append(int(row['num_agents']))
            runtime.append(float(row['runtime']))
            solution_cost.append(int(row['solution cost']))
            
    with open(memory_results_filepath, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            ram_usage.append(float(row['PeakMemoryMB']))
            
    
    return num_agents, runtime, solution_cost, ram_usage   
    
def plot_scatter_agents_runtime(x, y):
    """
    Inputs:
        x[]: List of x values (number of agents).
        y[]: List of y values (runtime).
    Outputs:
        None
    Description:
        This function generates a scatter plot using the provided x and y values,
        with an overlay showing average runtime ±3 for each number of agents.
    """
    plt.figure(figsize=(10, 6))
    
    # Create scatter plot of raw data
    plt.scatter(x, y, c='r', marker='x', alpha=0.5, label='Individual runs')
    
    # Calculate average runtime for each unique number of agents
    unique_agents = sorted(list(set(x)))
    avg_runtime = []
    std_runtime = []
    
    for agent_count in unique_agents:
        # Initialize empty list to store runtimes for this agent count
        runtimes = []
        # Loop through each data point
        for i in range(len(x)):
            # Check if this data point is for the current agent count
            if x[i] == agent_count:
            # If so, add its runtime to our list
                runtimes.append(y[i])
        
        avg_runtime.append(np.mean(runtimes))
        std_runtime.append(np.std(runtimes))
    
    # Plot average line
    plt.plot(unique_agents, avg_runtime, 'b-', label='Average runtime')
    
    # Plot error bounds (±3)
    plt.fill_between(unique_agents, 
                    [max(0, avg - 3) for avg in avg_runtime],
                    [avg + 3 for avg in avg_runtime],
                    color='b', alpha=0.2, label='±3 bound')
    
    plt.title('Runtime vs Number of Agents')
    plt.xlabel('Number of Agents')
    plt.ylabel('Runtime (s)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('./graphing/runtime_vs_agents_scatter.png')

def plot_scatter_agents_solution_cost(x, y):
    """
    Inputs:
        x[]: List of x values (number of agents).
        y[]: List of y values (solution cost).
    Outputs:
        None
    Description:
        This function generates a scatter plot using the provided x and y values.
    """
    plt.figure(figsize=(10, 6))
    
    # Create scatter plot of raw data
    plt.scatter(x, y, c='r', marker='x', alpha=0.5, label='Individual runs')
    
    plt.title('Solution Cost vs Number of Agents')
    plt.xlabel('Number of Agents')
    plt.ylabel('Solution Cost')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('./graphing/solution_cost_vs_agents_scatter.png')
    
def plot_scatter_ramuse_numagents(x, y):
    """
    Inputs:
        x[]: List of x values (number of agents).
        y[]: List of y values (RAM usage).
    Outputs:
        None
    Description:
        This function generates a scatter plot using the provided x and y values.
    """
    plt.figure(figsize=(10, 6))
    
    # Create scatter plot of raw data
    plt.scatter(x, y, c='r', marker='x', alpha=0.5, label='Individual runs')
    
    plt.title('RAM Usage vs Number of Agents')
    plt.xlabel('Number of Agents')
    plt.ylabel('RAM Usage (MB)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig('./graphing/ram_usage_vs_agents_scatter.png')

if __name__ == "__main__":
    num_agents = []
    runtime = []
    solution_cost = []
    ram_usage = []
    
    clean_data("./graphing/runtests.csv", "./graphing/memory_results.csv")
    
    # ramuse_data = './graphing/memory_results.csv'
    cleaned_runtests = './graphing/runtests_cleaned.csv'
    cleaned_ramuse = './graphing/memory_results_cleaned.csv'
    
    num_agents, runtime, solution_cost, ram_usage = extract_info(cleaned_runtests, cleaned_ramuse)
    plot_scatter_agents_runtime(num_agents, runtime)
    plot_scatter_agents_solution_cost(num_agents, solution_cost)
    plot_scatter_ramuse_numagents(num_agents, ram_usage)
    