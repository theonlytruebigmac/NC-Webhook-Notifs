# set base image
FROM alpine:3.18.5

# extra data
LABEL version="1.0.0"
LABEL description="First image with Dockerfile"

# setting working dir
WORKDIR /app

# update sources list and install packages
RUN apk update && \
    apk add --no-cache git bash nano tmux wget curl python3 py3-pip musl-locales musl-locales-lang && \
    rm -rf /var/cache/apk/*

# set environment variables
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# copying over requirements file
COPY requirements.txt requirements.txt

# installing pip requirements
RUN pip3 install -r requirements.txt

# set environment variables during build
ARG DISCORD_WEBHOOK_URL
ARG TEAMS_WEBHOOK_URL

# set environment variables
ENV DISCORD_WEBHOOK_URL=$DISCORD_WEBHOOK_URL
ENV TEAMS_WEBHOOK_URL=$TEAMS_WEBHOOK_URL

# exposing port 5000
EXPOSE 5000

# copy over project directories
COPY . .

# setting entry point
RUN chmod u+x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
