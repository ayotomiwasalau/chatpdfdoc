import sys
from pipeline import Pipeline
import os
import asyncio

def main():

    filepaths = './data/resume.pdf'
    run_id = Pipeline(filepaths).run()
    print(f"run_id={run_id}")

if __name__ == "__main__":
    main()