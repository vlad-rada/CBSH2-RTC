import subprocess
import os
import random
import psutil
import time
import csv

results_csv = "./cbs_output/final_results.csv"
write_header = not os.path.exists(results_csv)
runtest_path = "./cbs_output/runtests.csv"
not_valgrind_path = "./cbs_output/runtests_not_valgrind.csv"

processes = []


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

with open(not_valgrind_path, "w", newline="") as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(headers)

#look into psutil to get peak memory usage 
#take in 

input_dir = "./maps/maps"

input_files = sorted(os.listdir(input_dir))

output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

executable = "./cbs"


#loop through "input" folder to grab each map file 
for filename in input_files:
    if not filename.endswith(".map"):
        continue
    # Skip files that are not .map
    
    
    input_path = os.path.join(input_dir, filename)

    # agents folder will be in ./inputs/(filename)/
    # for example if we have the inputs/Berlin_1_256.map, the scenes are in .inputs/Berlin_1_256/ 

    #run the command
    #loop to increase number of agents
    process = None

    #TODO: CHANGE TO 25
    for scene in range(1,6):
        timeoutCounter = 0

        
        #INSERT FUNCTION TO CALL AGENT FILE CHANGER HERE. WILL CHANGE agents.txt FILE

        ### pull y agents randomly from a randomly chosen scen file

        chosenScen = filename.split(".")[0] + "-even-" + str(scene) + ".scen"
        chosenScenTwo = os.path.join("./scenesinput/"+ filename.split(".")[0], chosenScen)
        print(filename)
        
        for agents in range(1,850):

            print("Running " + filename + " with scene " + chosenScenTwo + " and " + str(agents) + " agents")
            output_path = "./cbs_output/paths.txt"
            numAgents = str(agents)
            args = [executable, "-m", input_path, "-a", chosenScenTwo, "-o", "./cbs_output/runtests_not_valgrind.csv", "--outputPaths=" + 
                    output_path,"-k", numAgents, "-t", "10", "--heuristics", "Zero", "--prioritizingConflicts", "0", 
                    "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", 
                    "--mutexReasoning", "0", "--targetReasoning", "0", "--sip", "0"]
            print(args)
            print(numAgents)
            
            #run process.
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append(process)

            '''
            old memory logging:

            while process.poll() is None:
                try:
                    mem = p.memory_info().rss  
                    peak_memory = max(peak_memory, mem)
                except psutil.NoSuchProcess:
                    break
                time.sleep(0.1)  # frequency of polling
                
            # bytes to MB
            peak_memory_MB = peak_memory / (1024 ** 2)
            '''


            # copy last line from runtest.csv to final_results.csv  -- important to stop data from being overriden 
            # by valgrind later

            with open(runtest_path, "r") as src, open(results_csv, "a", newline="") as dst:
                last_line = list(csv.reader(src))[-1]
                csv.writer(dst).writerow(last_line)

            # NOW SAFE TO RUN VALGRIND
            # FIRST CHECK FOR TIMEOUT -- IF IT TIMES OUT WE DONT CARE ABT VALGRIND OUTPUT

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
                                print(f"Timeout occurred. Timeout counter: {timeoutCounter}")
                                break
            except Exception as e:
                print(f"Error reading runtests.csv: {e}")

            #RUN CACHEGRIND W NO ARGS
            
            # teststring = f"{filename} {scene} {numAgents}"
            # /valgrind_outputs/cachegrind/[numAgents]/Boston_0_256.map.S1.out
            os.makedirs(f"./valgrind_outputs/cachegrind/agents_{numAgents}", exist_ok=True)
            cachegrindoutfile = f"--cachegrind-out-file=./valgrind_outputs/cachegrind/agents_{numAgents}/{filename}_{scene}.out"
            
            
            
            args = ["valgrind", "--tool=cachegrind", cachegrindoutfile, executable, "-m", input_path, "-a", chosenScenTwo, "-o", "./cbs_output/runtests.csv", "--outputPaths=" + 
                    output_path,"-k", numAgents, "-t", "5", "--heuristics", "Zero", "--prioritizingConflicts", "0", 
                    "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", 
                    "--mutexReasoning", "0", "--targetReasoning", "0", "--sip", "0"]
            
            
            
            #run process.
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append(process)

            # print(stderr.decode())
            # p = psutil.Process(process.pid)  

            #RUN CACHEGRIND W CACHE SIM ARGS
            # /valgrind_outputs/cachesim/[numAgents]/Boston_0_256.map.S1.out
            os.makedirs(f"./valgrind_outputs/cachesim/agents_{numAgents}", exist_ok=True)
            cachesimoutfile = f"--cachegrind-out-file=./valgrind_outputs/cachesim/agents_{numAgents}/{filename}_{scene}.out"


            args = ["valgrind", "--tool=cachegrind", "--cache-sim=yes", cachesimoutfile, executable, "-m", input_path, "-a", chosenScenTwo, "-o", "./cbs_output/runtests.csv", "--outputPaths=" + 
                    output_path,"-k", numAgents, "-t", "5", "--heuristics", "Zero", "--prioritizingConflicts", "0", 
                    "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", 
                    "--mutexReasoning", "0", "--targetReasoning", "0", "--sip", "0"]
            
            #run process.
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    
            processes.append(process)
      

            #RUN MASSIF W NO ARGS
            os.makedirs(f"./valgrind_outputs/massif/agents_{numAgents}", exist_ok=True)
            massifoutfile = f"--massif-out-file=./valgrind_outputs/massif/agents_{numAgents}/{filename}_{scene}.out"

            args = ["valgrind", "--tool=massif", massifoutfile, executable, "-m", input_path, "-a", chosenScenTwo, "-o", "./cbs_output/runtests.csv", "--outputPaths=" + 
                    output_path,"-k", numAgents, "-t", "5", "--heuristics", "Zero", "--prioritizingConflicts", "0", 
                    "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", 
                    "--mutexReasoning", "0", "--targetReasoning", "0", "--sip", "0"]
            
            #run process.
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append(process)


            #RUN MASSIF W STACKS ON
            os.makedirs(f"./valgrind_outputs/massif_stacks/agents_{numAgents}", exist_ok=True)
            massif_stacksoutfile = f"--massif-out-file=./valgrind_outputs/massif_stacks/agents_{numAgents}/{filename}_{scene}.out"

            args = ["valgrind", "--tool=massif", "--stacks=yes", massif_stacksoutfile, executable, "-m", input_path, "-a", chosenScenTwo, "-o", "./cbs_output/runtests.csv", "--outputPaths=" + 
                    output_path,"-k", numAgents, "-t", "5", "--heuristics", "Zero", "--prioritizingConflicts", "0", 
                    "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", 
                    "--mutexReasoning", "0", "--targetReasoning", "0", "--sip", "0"]
            
            #run process.
            process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append(process)

for process in processes:
    stdout, stderr = process.communicate()