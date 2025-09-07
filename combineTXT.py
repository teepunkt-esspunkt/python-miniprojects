#simple combining all .txt files into one
import os

def combine_txt_files(output_file="combined.txt"):
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # List all .txt files in the directory (excluding the output file)
    txt_files = [f for f in os.listdir(script_dir) if f.endswith(".txt") and f != output_file]

    with open(os.path.join(script_dir, output_file), "w", encoding="utf-8") as outfile:
        for filename in txt_files:
            file_path = os.path.join(script_dir, filename)
            with open(file_path, "r", encoding="utf-8") as infile:
                content = infile.read()
                outfile.write(f"--- {filename} ---\n")  # Optional: mark the file's start
                outfile.write(content + "\n\n")

    print(f"Combined {len(txt_files)} files into {output_file}.")

if __name__ == "__main__":
    combine_txt_files()

