import sys
from pipeline import Pipeline
import os
import asyncio

os.environ["OPENAI_API_KEY"] = "voc-16895601641598743158105686d56d750bb86.12485774"
os.environ["OPENAI_API_BASE"] = "https://openai.vocareum.com/v1"
def main():

    filepaths = './data/resume.pdf'
    run_id = Pipeline(filepaths).run()
    print(f"run_id={run_id}")

if __name__ == "__main__":
    main()