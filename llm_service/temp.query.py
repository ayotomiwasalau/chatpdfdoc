from query import Query

import os
os.environ["OPENAI_API_KEY"] = "voc-16895601641598743158105686d56d750bb86.12485774"
os.environ["OPENAI_API_BASE"] = "https://openai.vocareum.com/v1"

def main():
    query = Query()
    print(query.query("Who is Ayotomiwa Salau girlfriend?"))

if __name__ == "__main__":
    main()