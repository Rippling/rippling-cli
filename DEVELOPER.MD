# Setup rippling-cli for development
Pre-requisites:
- Python 3.10 or higher
- pip must be installed
- poetry must be installed
1. Clone the repository
2. Run this command to create a virtual environment and install all the dependencies
```
python -m pip install -e .
```
3. Activate your virtual environment by running this command
```
source .venv/bin/activate
```
4. Run this command to view if your setup is complete
```
python ./rippling_cli/cli/main.py 
```
You should see this screenshot if your setup is complete
![image]()