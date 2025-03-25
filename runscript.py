import subprocess
import os
import random

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

    for y in range(50):

        for x in range(10):
        #INSERT FUNCTION TO CALL AGENT FILE CHANGER HERE. WILL CHANGE agents.txt FILE

        ### pull y agents randomly from a randomly chosen scen file

            chosenScen = filename.split(".")[0] + "-even-" + str(random.randint(1,25)) + ".scen"
            chosenScenTwo = os.path.join("scenesinput", chosenScen)

            scenFile = open(chosenScenTwo, "r")
            print("Scene file: " + chosenScenTwo)

            allLines = []

            for line in scenFile:
                if line[0] == "v":
                    continue
                allLines.append(line)

            indices = random.sample(range(1,26), y)
            outputFile = open("agents.txt","w")
            outputFile.write("version 1\n")
            for index in indices:
                outputFile.write(allLines[index])

         

            print("Running " + filename + " with " + str(y) + " agents")
            output_path = os.path.join(output_dir, f"{filename}{counter}")
            numAgents = str(y)
            args = ["time", executable, "-m", input_path, "-a", "agents.txt", "-o", "runtests.csv", "--outputPaths=" + output_path,"-k", numAgents, "-t", "600", "--heuristics", "Zero", "--prioritizingConflicts", "0", "--bypass", "0", "--disjointSplitting", "0", "--rectangleReasoning", "None", "--corridorReasoning", "None", "--mutexReasoning", "0", "--targetReasoning", "0"]
            result = subprocess.run(args, capture_output=True, text=True)
            counter = counter + 1
