FROM python:3-slim

COPY . /opt/source-code
WORKDIR /opt/source-code
ENV FLASK_RUN_HOST=0.0.0.0
RUN pip3 --no-cache-dir install -r requirements.txt
RUN apt-get update
RUN apt-get install -y locales locales-all
ENV LC_TIME de_DE.UTF-8
EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["run.py"]