import re
import os

def remove_brackets_from_file(input_file, output_file=None):
    # If no output file is provided, overwrite the original
    if output_file is None:
        output_file = input_file

    with open(input_file, "r", encoding="utf-8") as infile:
        text = infile.read()

    # Remove all text within {} and [] including the brackets
    cleaned_text = re.sub(r"\{.*?\}|\[.*?\]", "", text, flags=re.DOTALL)

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(cleaned_text)

    print(f"Brackets and content removed: {input_file} -> {output_file}")

if __name__ == "__main__":
    # Get the script's folder
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Specify your file relative to the script's folder
    filename = os.path.join(script_dir, "combined.txt")  # <-- Replace with your file name
    remove_brackets_from_file(filename)
