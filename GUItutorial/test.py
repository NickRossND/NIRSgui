import glob
import os

# Path to your ASC files (change as needed)
input_folder = "G:/Shared drives/NickRoss_PhDWork/HematomaPhantoms/nigromix11-10-23_newPhantom/250813-2-Copy"
output_folder = "G:/Shared drives/NickRoss_PhDWork/HematomaPhantoms/nigromix11-10-23_newPhantom/250813-2-Copy"

os.makedirs(output_folder, exist_ok=True)

for file_path in glob.glob(os.path.join(input_folder, "*.asc")):
    with open(file_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    skip_count = 0
    found_frequency = False

    for line in lines:
        if not found_frequency and line.startswith("Frequency"):
            found_frequency = True
            skip_count = 16  # number of lines to skip
            new_lines.append(line)  # keep the 'Frequency' line itself
        elif found_frequency and skip_count > 0:
            skip_count -= 1  # skip these lines
        else:
            new_lines.append(line)

    # Save modified file to new folder
    output_path = os.path.join(output_folder, os.path.basename(file_path))
    with open(output_path, "w") as f:
        f.writelines(new_lines)

print("Processing complete.")
