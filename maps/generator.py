"""
Generator.py

This module will prompt the user for a map area and generate a map for use in CBS.
"""

import random


def prompts():
    """
    Input: None
    Output: Array of strings: [width, height, blockage probability]
    Description: This function will prompt the user for input regarding the map area.
        It will also ask the user for a blockage probability to apply to each tile
        in the map. The function will return an array of strings containing the
        user input.
    """
    
    returns = [] # Array storing width and height
    
    # Map width prompt
    width = input("Enter the map width[min=4 max=512]: ")
    while not (4 <= int(width) <= 512):
        width = input("Invalid input. Enter the map width[min=4 max=512]: ")
    returns.append(width)
    
    # Map height prompt
    height = input("Enter the map height[min=4 max=512]: ")
    while not (4 <= int(height) <= 512):
        height = input("Invalid input. Enter the map height[min=4 max=512]: ")
    returns.append(height)
    
    # Map blockage probability prompt
    blockage = input("Enter the blockage probability[0.0-1.0]: ")
    while not (0.0 <= float(blockage) <= 1.0):
        blockage = input("Invalid input. Enter the blockage probability[0.0-1.0]: ")
    returns.append(blockage)
    
    return returns

def generate_map(user_inputs):
    """
    Input: Array of strings: [width, height, blockage probability]
    Output: Two dimensional array of characters
    Description: This function will generate a map based on the user input. For
        clear areas, the array position will contain a '.' character. For blocked
        areas, the array position will contain a '@' character.
    """
    width = int(user_inputs[0])
    height = int(user_inputs[1])
    blockage_probability = float(user_inputs[2])
    

    # Initialize the map array with clear areas
    map_array = [['.' for _ in range(width)] for _ in range(height)]
    
    # Randomly assign blocked areas based on the blockage probability
    for i in range(height):
        for j in range(width):
            if random.random() < blockage_probability:
                map_array[i][j] = '@'
    
    # Ensure that for any row or column, there is at least one clear area
    for i in range(height):
        if all(map_array[i][j] == '@' for j in range(width)):
            map_array[i][random.randint(0, width - 1)] = '.'
    for j in range(width):
        if all(map_array[i][j] == '@' for i in range(height)):
            map_array[random.randint(0, height - 1)][j] = '.'
    
    
    return map_array

def export_map(map_array, blockage_probability):
    """
    Input: Two dimensional array of characters, map probability
    Output: None
    Description: This function will export the map to a file. The file will be
        named in the format "[width]x[height][probability].map".
    """
    # Extract width and height from the map array
    height = len(map_array)
    width = len(map_array[0]) if height > 0 else 0
    
    # Create the filename based on the map dimensions and blockage probability
    filename = f"{width}x{height}_{blockage_probability}.map"
    
    # Write the initial information before the map and write map to file
    with open(filename, 'w') as f:
        f.write("type octile\n")
        f.write(f"height {height}\n")
        f.write(f"width {width}\n")
        f.write("map\n")
        
        for row in map_array:
            f.write(''.join(row) + '\n')
    
    
    print("Map exported to", filename)

def main():
    """
    Main function to run the map generator.
    """
    
    user_inputs = prompts()
    map_array = generate_map(user_inputs)
    export_map(map_array, float(user_inputs[2]))

if __name__ == "__main__":
    main()