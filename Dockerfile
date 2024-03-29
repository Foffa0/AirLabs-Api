FROM python:3.8-slim

ARG UNAME=appuser
ARG UID=1000
ARG GID=100
RUN groupadd -g $GID -o $UNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/sh $UNAME
RUN apt-get update
RUN apt-get install -y locales locales-all
# USER $UNAME

# CMD /bin/sh

COPY --chown=$UID:$GID . /opt/source-code
WORKDIR /opt/source-code
ENV FLASK_RUN_HOST=0.0.0.0
RUN pip3 --no-cache-dir install -r requirements.txt
ENV LC_TIME de_DE.UTF-8
EXPOSE 5000

ENTRYPOINT ["./gunicorn.sh"]

#CMD ["gunicorn", "app:create_app()", "-w", "1", "--threads", "2", "-b", "0.0.0.0:5000"]