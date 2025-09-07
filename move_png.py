#to clean up some messed up structure
import os
import shutil

# Absolute path to the current script
#script_path = os.path.abspath(__file__)

# Directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

for root, dirs, files in os.walk(script_dir):
    if root == script_dir:
        continue

    for file in files:
        file_path = os.path.join(root, file)
        destination = os.path.join(script_dir, file)

        if os.path.exists(destination):
            name, ext = os.path.splitext(file)
            counter = 1
            while os.path.exists(destination):
                destination = os.path.join(script_dir, f"{name}_{counter}{ext}")
                counter += 1

        shutil.move(file_path, destination)


print("done:", script_dir)
