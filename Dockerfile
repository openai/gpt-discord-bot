FROM python:slim
RUN apt-get update && apt-get dist-upgrade -y 
RUN apt-get install git -y
RUN pip install numpy
RUN git clone https://github.com/openai/gpt-discord-bot
WORKDIR gpt-discord-bot
RUN pip install -r requirements.txt
COPY .env.example /.env
CMD ["python", "-m", "src.main"]




