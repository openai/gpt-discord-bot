FROM ubuntu

RUN apt-get update && apt-get dist-upgrade -y 

RUN apt-get install git python3-pip

RUN git clone https://github.com/openai/gpt-discord-bot

WORKDIR gpt-discord-bot

COPY .env.example .

CMD ["python -m src.main"]