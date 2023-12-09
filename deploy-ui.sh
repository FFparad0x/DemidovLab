#/bin/bash

sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.10 -y
sudo apt install python3.10-venv -y
python3.10 --version

git clone https://github.com/FFparad0x/DemidovLab.git
cd DemidovLab/ui

# activate venv
python3.10 -m venv venv
source venv/bin/activate
pip install -r req.txt
TARGET_HOST="10.2.58.4:8000"
uvicorn main:app --port 8080
