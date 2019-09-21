FROM python:3.6
RUN useradd -m -s /bin/bash ayrabo
USER ayrabo
ENV SRC_DIR="/home/ayrabo/src" PATH="/home/ayrabo/.local/bin:$PATH"
RUN mkdir $SRC_DIR
WORKDIR $SRC_DIR
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt
