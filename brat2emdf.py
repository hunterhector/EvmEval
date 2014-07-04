#!/usr/bin/python 

"""
    A simple piece of python code that could convert the Brat annotation
tool format into Event Mention Detection format for easy evaluation. For
detailed features and usage please refer to the README file
"""
import argparse
import logging

def main():
    parser = argparse.ArgumentParser(description="Brat to EMDF converter")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d","directory",help="directory of the annotations")
    group.add_argument("-f","basename",help="single base name of one file")
    group.add_argument("-l","filelist",help="list of files that will be processed")

    args = parser.parse_args() 

if __name__ == "__main__":
    main()


