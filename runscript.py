import subprocess
import os
import random
import psutil
import time
import csv
import shutil

# results_csv = "./cbs_output/final_results.csv"
# write_header = not os.path.exists(results_csv)
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

# Refresh the directories
try:
    shutil.rmtree("./valgrind_outputs/cleaned")
    shutil.rmtree("./valgrind_outputs/cachesim")
    shutil.rmtree("./valgrind_outputs/massif_stacks")
except OSError as e:
    print(f"Error: {e.strerror}")
os.makedirs("./valgrind_outputs/cleaned", exist_ok=True)
os.makedirs("./valgrind_outputs/cachesim", exist_ok=True)
os.makedirs("./valgrind_outputs/massif_stacks", exist_ok=True)




if os.path.exists(runtest_path):
  os.remove(runtest_path)

if os.path.exists(not_valgrind_path):
    os.remove(not_valgrind_path)

with open(runtest_path, "w", newline="") as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(headers)

with open(not_valgrind_path, "w", newline="") as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(headers)

#look into psutil to get peak memory usage 
#take in 

input_dir = "./maps"


output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

executable = "./cbs"


#loop through "input" folder to grab each map file 
for filename in os.listdir(input_dir):
    # Skip files that are not .map

    if not filename.endswith(".map"):
        continue
    

    input_path = os.path.join(input_dir, filename)
    
    # Set number of agents here
    num_agents = 150
    
    # Set number of scenes here
    num_scenes = 5

    for scene in range(1, num_scenes):

        chosenScen = os.path.join("./scenesinput/"+ filename.split(".")[0], filename.split(".")[0] + "-even-" + str(scene) + ".scen")
        # print(filename)
        

        # continue
        for agents in range(1, num_agents):

            print("Running " + filename + " with scene " + chosenScen + " and " + str(agents) + " agents")
            output_path = "./cbs_output/paths.txt"
            numAgents = str(agents)
            args = [executable, "-m", input_path, "-a", chosenScen, "-o", "./cbs_output/runtests_not_valgrind.csv", "--outputPaths=" + 
                    output_path,"-k", numAgents, "-t", "30", "--heuristics", "Zero", "--prioritizingConflicts", "0", 
                    "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", 
                    "--mutexReasoning", "0", "--targetReasoning", "0", "--sip", "0"]
            # print(args)
            # print(numAgents)
                        
            #run process.
            process1 = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append(process1)

            # stdout, stderr = process1.communicate()
            # process1.wait()
            
            # copy last line from runtest.csv to final_results.csv  -- important to stop data from being overriden 
            # by valgrind later

            # with open(runtest_path, "r") as src, open(results_csv, "a", newline="") as dst:
            #     last_line = list(csv.reader(src))[-1]
            #     csv.writer(dst).writerow(last_line)

            # NOW SAFE TO RUN VALGRIND
            # FIRST CHECK FOR TIMEOUT -- IF IT TIMES OUT WE DONT CARE ABT VALGRIND OUTPUT

            # Check if the solution cost is -2 (timeout)
            try:
                with open("./cbs_output/runtests_not_valgrind.csv", "r") as csvfile:
                    reader = csv.reader(csvfile)
                    rows = list(reader)
                    if len(rows) > 1:  # Ensure there's at least one data row
                        last_row = rows[-1]
                        solution_cost_index = headers.index("solution cost")
                        try:
                            solution_cost = last_row[solution_cost_index]
                            if solution_cost == "-2" or solution_cost == "-1":
                                break
                        except ValueError:
                            print(f"Error: 'solution cost' not found in headers.")
                            continue
            except Exception as e:
                print(f"Error reading runtests.csv: {e}")
            

            # # Callgrind process creation
            # os.makedirs(f"./valgrind_outputs/callgrind/agents_{numAgents}", exist_ok=True)
            # callgrindoutfile = f"--callgrind-out-file=./valgrind_outputs/callgrind/agents_{numAgents}/{filename}_{scene}.out"
            # args = ["valgrind", "--tool=callgrind", "--cache-sim=yes", 
            #          "--I1=32768,8,64", "--D1=49152,12,64", "--LL=2097152,16,64",
            #         callgrindoutfile, executable, "-m", input_path, "-a", chosenScen, "-o", "./cbs_output/runtests.csv", "--outputPaths=" +
            #         output_path,"-k", numAgents, "-t", "60", "--heuristics", "Zero", "--prioritizingConflicts", "0", 
            #         "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", 
            #         "--mutexReasoning", "0", "--targetReasoning", "0", "--sip", "0"]
            
            
            # #run process.
            # process2 = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # processes.append(process2)


            # Cachegrind process creation
            os.makedirs(f"./valgrind_outputs/cachesim/agents_{numAgents}", exist_ok=True)
            cachesimoutfile = f"--cachegrind-out-file=./valgrind_outputs/cachesim/agents_{numAgents}/{filename}_{scene}.out"
            args = ["valgrind", "--tool=cachegrind", "--cache-sim=yes", 
                     "--I1=32768,8,64", "--D1=49152,12,64", "--LL=2097152,16,64",
                    cachesimoutfile, executable, "-m", input_path, "-a", chosenScen, "-o", "./cbs_output/runtests.csv", "--outputPaths=" + 
                    output_path,"-k", numAgents, "-t", "60", "--heuristics", "Zero", "--prioritizingConflicts", "0", 
                    "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", 
                    "--mutexReasoning", "0", "--targetReasoning", "0", "--sip", "0"]
            #run process.
            process3 = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    
            processes.append(process3)


            # Massif process creation (Stacks option enabled)
            os.makedirs(f"./valgrind_outputs/massif_stacks/agents_{numAgents}", exist_ok=True)
            massif_stacksoutfile = f"--massif-out-file=./valgrind_outputs/massif_stacks/agents_{numAgents}/{filename}_{scene}.out"
            args = ["valgrind", "--tool=massif", "--stacks=yes", massif_stacksoutfile, executable, "-m", input_path, "-a", chosenScen, "-o", "./cbs_output/runtests.csv", "--outputPaths=" + 
                    output_path,"-k", numAgents, "-t", "60", "--heuristics", "Zero", "--prioritizingConflicts", "0", 
                    "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", 
                    "--mutexReasoning", "0", "--targetReasoning", "0", "--sip", "0"]
            #run process.
            process4 = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append(process4)
            
            
            
            for process in processes:
                stdout, stderr = process.communicate()
                process.wait()
            processes.clear()
            
            
            # Create directories for cleaned valgrind outputs
            os.makedirs(f"./valgrind_outputs/cleaned/cachesim/agents_{numAgents}", exist_ok=True)
            os.makedirs(f"./valgrind_outputs/cleaned/massif_stacks/agents_{numAgents}", exist_ok=True)
            
            from pathlib import Path
            output_path = Path(f"./valgrind_outputs/cleaned/cachesim/agents_{numAgents}/{filename}_{scene}.out.clean")
            with open(output_path, "w") as outfile:
                subprocess.run(
                    ["cg_annotate", f"./valgrind_outputs/cachesim/agents_{numAgents}/{filename}_{scene}.out"],
                    stdout=outfile,
                    stderr=subprocess.PIPE
                )
            output_path = Path(f"./valgrind_outputs/cleaned/massif_stacks/agents_{numAgents}/{filename}_{scene}.out.clean")
            with open(output_path, "w") as outfile:
                subprocess.run(
                    ["ms_print", f"./valgrind_outputs/massif_stacks/agents_{numAgents}/{filename}_{scene}.out"],
                    stdout=outfile,
                    stderr=subprocess.PIPE
                )
