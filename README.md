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



- schema mgt
- review where the chat and uploaded doc info is stored
- delete doc from v-db



- add unit tests? done





- ? another database
prod: upload file to object storage ex. s3



python3 -m venv .ragenv
chmod +x .ragenv/bin/activate
source .ragenv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirement.txt

python -m uvicorn main:app --reload

python -m pytest