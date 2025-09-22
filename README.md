# TODO
- finalize the pipeline service - done
- set up the db properly - done
- set up the llm classes and methods - done
- set up fast api - done
- set up front end - done
- make the chat stateful -done
- add doc stateful - done
- stream data to front end - done
- organize file structure - done
- ? provide query api w & w/o stremaing capability - done
- delete temp files - done
- handle config - done
- work on the chunking size, search cnt - done
- handling query with history of chat and responses - done
- api versions - done
- add swagger for documentation - done
- work on system prompt - done?
- add exception handling - done?
- add logging, more descriptive - done?
- Validating inputs - done?
- handle cred - done?
- add unit tests? done
- cleaner error returnv - done
- schema mgt - done
- new chat decision - done
- api key check - done
- work on system prompt - done?


- review where the chat and uploaded doc info is stored
- delete doc from v-db
- ? another database json










prod: upload file to object storage ex. s3



python3 -m venv .ragenv
chmod +x .ragenv/bin/activate
source .ragenv/bin/activate

export OPENAI_API_KEY="api_key"

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirement.txt

python main.py

python -m uvicorn main:app --reload

python -m pytest