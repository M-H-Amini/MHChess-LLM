FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

