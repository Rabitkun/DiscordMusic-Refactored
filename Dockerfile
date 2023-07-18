FROM python:3.11-slim-bullseye

WORKDIR /app

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

COPY req.txt req.txt
RUN pip3 install -r req.txt

COPY . .

CMD [ "python3", "main.py"]