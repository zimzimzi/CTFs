FROM python:3
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
WORKDIR /code
COPY ./code/requirements.txt ./
RUN pip install -r requirements.txt
COPY ./code/ ./
EXPOSE 80