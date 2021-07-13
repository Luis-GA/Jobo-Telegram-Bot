FROM python:3.8-slim
WORKDIR /jobo
COPY jobo_bot.py NEAS.py requirements.txt ./
RUN pip install -r requirements.txt

CMD [ "python", "jobo_bot.py" ]