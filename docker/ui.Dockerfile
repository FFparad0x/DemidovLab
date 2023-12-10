FROM python:3.10-bullseye
RUN git clone https://github.com/FFparad0x/DemidovLab.git;cd DemidovLab/api;python3.10 -m venv venv;source venv/bin/activate;pip install -r req-serv.text;
ENV TARGET_HOST="127.0.0.1:8081"
WORKDIR /DemidovLab/ui
EXPOSE 8080
CMD ["/bin/bash","-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]
