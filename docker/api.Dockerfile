FROM python:3.10-bullseye
RUN git clone https://github.com/FFparad0x/DemidovLab.git;cd DemidovLab/api;python3.10 -m venv venv;source venv/bin/activate;pip install -r req-serv.text;
WORKDIR /DemidovLab/api
EXPOSE 8081
CMD ["/bin/bash","-c", "uvicorn main:app --host 0.0.0.0 --port 8081"]