import subprocess
import os
import random
import psutil
import time
import csv

results_csv = "./cbs_output/memory_results.csv"
write_header = not os.path.exists(results_csv)
runtest_path = "./cbs_output/runtests.csv"


"""
				"runtime,#high-level expanded,#high-level generated,#low-level expanded,#low-level generated," <<
				 "solution cost,min f value,root g value,root f value," <<
				 "#adopt bypasses," <<
				 "standard conflicts,rectangle conflicts,corridor conflicts,target conflicts,mutex conflicts," <<
				 "#merge MDDs,#solve 2 agents,#memoization," <<
				 "runtime of building heuristic graph,runtime of solving MVC," <<
				 "runtime of detecting conflicts," <<
				 "runtime of rectangle conflicts,runtime of corridor conflicts,runtime of mutex conflicts," <<
				 "runtime of building MDDs,runtime of building constraint tables,runtime of building CATs," <<
				 "runtime of path finding,runtime of generating child nodes," <<
				 "preprocessing runtime,solver name,instance name,num_agents" <<
"""

# Clear the runtest csv
# Extract headers from comment and write to runtest.csv
headers = ["runtime", "#high-level expanded", "#high-level generated", "#low-level expanded", "#low-level generated", 
		   "solution cost", "min f value", "root g value", "root f value",
		   "#adopt bypasses",
		   "standard conflicts", "rectangle conflicts", "corridor conflicts", "target conflicts", "mutex conflicts", 
		   "#merge MDDs", "#solve 2 agents", "#memoization", 
		   "runtime of building heuristic graph", "runtime of solving MVC", 
		   "runtime of detecting conflicts",
		   "runtime of rectangle conflicts", "runtime of corridor conflicts", "runtime of mutex conflicts",
		   "runtime of building MDDs", "runtime of building constraint tables", "runtime of building CATs",
		   "runtime of path finding", "runtime of generating child nodes",
		   "preprocessing runtime", "solver name", "instance name", "num_agents"]

with open(runtest_path, "w", newline="") as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(headers)

#look into psutil to get peak memory usage 
#take in 

input_dir = "inputs"
input_files = sorted(os.listdir(input_dir))

output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)


executable = "./cbs"

counter = 0

#loop through "input" folder to grab each map file 
for filename in input_files:
    input_path = os.path.join(input_dir, filename)

    # agents folder will be in ./inputs/(filename)/
    # for example if we have the inputs/Berlin_1_256.map, the scenes are in .inputs/Berlin_1_256/ 

    #run the command
    #loop to increase number of agents

    for scene in range(1,26):
        timeoutCounter = 0

        
        #INSERT FUNCTION TO CALL AGENT FILE CHANGER HERE. WILL CHANGE agents.txt FILE

        ### pull y agents randomly from a randomly chosen scen file

        chosenScen = filename.split(".")[0] + "-even-" + str(scene) + ".scen"
        chosenScenTwo = os.path.join("scenesinput", chosenScen)

        for agents in range(1,150):
            if timeoutCounter > 0:
                break

            print("Running " + filename + " with scene " + chosenScenTwo + " and " + str(agents) + " agents")
            output_path = os.path.join(output_dir, f"{filename}{counter}")
            numAgents = str(agents)
            args = [executable, "-m", input_path, "-a", chosenScenTwo, "-o", "./cbs_output/runtests.csv", "--outputPaths=" + 
                    output_path,"-k", numAgents, "-t", "10", "--heuristics", "Zero", "--prioritizingConflicts", "0", 
                    "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", 
                    "--mutexReasoning", "0", "--targetReasoning", "0", "--sip", "0"]
            
            #run process. collect resource data with psutil
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p = psutil.Process(process.pid)
            peak_memory = 0  
            
        

            while process.poll() is None:
                try:
                    mem = p.memory_info().rss  
                    peak_memory = max(peak_memory, mem)
                except psutil.NoSuchProcess:
                    break
                time.sleep(0.1)  # frequency of polling

            # try:
            #     stdout, stderr = process.communicate(timeout=2)
             
            # except psutil.TimeoutExpired:
            #     print(f"Process timed out for {filename} with {y} agents.")
            #     exit()            # Check if the process completed successfully
                
            # bytes to MB
            peak_memory_MB = peak_memory / (1024 ** 2)

            # If this is the first iteration, open file in write mode to clear existing content
            if counter == 0:
                with open(results_csv, mode="w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["Filename", "AgentCount", "RunID", "PeakMemoryMB"])
            
            # Now append the actual data
            with open(results_csv, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([filename, agents, counter, peak_memory_MB])
            counter += 1


            # Check if the solution cost is -2 (timeout)
            try:
                with open("./cbs_output/runtests.csv", "r") as csvfile:
                    reader = csv.reader(csvfile)
                    rows = list(reader)
                    if len(rows) > 1:  # Ensure there's at least one data row
                        last_row = rows[-1]
                        solution_cost_index = headers.index("solution cost")
                        if len(last_row) > solution_cost_index:
                            solution_cost = last_row[solution_cost_index]
                            if solution_cost == "-2" or solution_cost == "-1":
                                timeoutCounter += 1
                                print(f"Timeout occurred. Timeout counter: {timeoutCounter}")
            except Exception as e:
                print(f"Error reading runtests.csv: {e}")
            
            