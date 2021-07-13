FROM python:3.9
ARG CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN apt-get update
WORKDIR /jobo
COPY jobo_bot.py NEAS.py requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD [ "python", "jobo_bot.py" ]
