import os
import sys

def get_script_path(): #the path to the actual called script
    return os.path.realpath(sys.argv[0])

def get_script_dir(): #the path to the actual called script directory
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def get_executing_file_dir(): #e.g. the path to the module file
    return os.path.realpath(__file__)

def get_executing_file_dir(): #e.g. the path to the folder the module is in
    return os.path.dirname(os.path.realpath(__file__))
