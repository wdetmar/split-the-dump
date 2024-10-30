#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "Davyd Maker"
__version__ = "1.3"

import os
import argparse
import time
import re

def save_file(content, directory, file_name):
    try:
        file_path = os.path.join(directory, f'{file_name}.sql')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(''.join(content))
    except IOError as e:
        print(f"Error writing file {file_path}: {e}")

def prepare_directory(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def process_file(input_file_path, output_dir, ignore_blank_lines):
    prepare_directory(output_dir)
    start_time = time.time()
    current_content = []
    current_file_name = None

    try:
        with open(input_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                processed_line = handle_line(line, ignore_blank_lines)
                if processed_line is None:
                    continue

                # Check for CREATE OR REPLACE or CREATE VIEW statements
                if re.search(r'\b(CREATE\s+TABLE\s+\w+|CREATE\s+VIEW\s+\w+)', processed_line, re.IGNORECASE):
                    # If we have a current statement, save it before starting a new one
                    if current_content:
                        save_file(current_content, output_dir, current_file_name)
                        current_content = []  # Reset current content

                    # Extract the file name and start accumulating content
                    current_file_name = re.search(r'\b(CREATE\s+TABLE\s+\w+|CREATE\s+VIEW\s+\w+)', processed_line, re.IGNORECASE).group(0)
                    current_file_name = current_file_name.split('(')[0].strip().replace(' ', '_')

                # Accumulate lines until the first );
                current_content.append(processed_line)
                if ');' in processed_line:
                    # Save the current statement to a file and reset
                    if current_content:
                        save_file(current_content, output_dir, current_file_name)
                        current_content = []
                        current_file_name = None  # Reset file name

            # Save remaining content if any
            if current_content:
                save_file(current_content, output_dir, f"split_file_{len(os.listdir(output_dir)) + 1}")
    except Exception as e:
        print(f"Error reading file {input_file_path}: {e}")

    return time.time() - start_time

def handle_line(line, ignore_blank_lines):
    if ignore_blank_lines and not line.strip():
        return None
    return line

def main():
    parser = argparse.ArgumentParser(description="Splits an SQL file into parts based on CREATE OR REPLACE and CREATE VIEW statements and the option to ignore blank lines.")
    parser.add_argument("-i", "--input-file", required=True, help="Path to the SQL file to be processed.")
    parser.add_argument("-o", "--output-dir", default=None, help="Directory where the split files will be saved. If not provided, a directory with the name of the input file is created.")
    parser.add_argument("-b", "--ignore-blank-lines", action='store_true', help="Ignore blank lines in the file (default: False).")

    args = parser.parse_args()

    if not args.output_dir:
        base_name = os.path.splitext(os.path.basename(args.input_file))[0]
        args.output_dir = os.path.join(os.getcwd(), base_name)

    elapsed_time = process_file(args.input_file, args.output_dir, args.ignore_blank_lines)

    print(f"\nExecution completed in {elapsed_time:.2f} seconds. Files saved in: {args.output_dir}")

if __name__ == "__main__":
    main()
