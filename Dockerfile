FROM python:3.8-slim

RUN useradd --create-home --shell /bin/bash app_user

RUN apt-get update

RUN apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /home/app_user

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

USER app_user

COPY . .

CMD ["bash"]