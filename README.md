# NC XML Receiver

## Description

The NC XML Receiver is a Flask web application that processes N-able N-Central SOAP notifications, normalizes the data, and sends it to Discord and Microsoft Teams webhooks.

  ![alt text](screenshots/Discord_Warn_Fail_example.png)

## Features

- Receives N-Central SOAP XML notifications via a HTTP POST request
- Normalizes XML notification data based on N-Central notification schema
- Sends normalized data to Discord or Microsoft Teams webhooks

## Getting Started - Building From Source

### Prerequisites

- Docker installed
- Docker Compose installed

### Usage

1. Clone the repository:

   ```bash
   git clone https://git.syschimp.com/osintnugget/nc-xml-receiver.git
   ```

2. Navigate to the project directory:

   ```bash
   cd nc-xml-receiver
   ```

3. Install pip requirements:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the flask app to test and modify:

   ```bash
   flask run -h localhost -p 5000
   ```

5. To run via a production WSGI, I use guincorn but you can serve the app with your preferred tool:

   ```bash
   gunicorn -w 8 -b 0.0.0.0:5000 app:app
   ```

## Getting Started - Building Docker Image

1. Modify your Dockerfile environment variables (Not needed if you plan on using a docker-compose.yml)

    ```dockerfile
    # set base image
    FROM alpine:3.18.5

    # extra data
    LABEL version="1.0.0"
    LABEL description="First image with Dockerfile"

    # setting working dir
    WORKDIR /app

    # update sources list and install packages
    RUN apk update && \
        apk add --no-cache git bash nano tmux wget curl python3 py3-pip   musl-locales musl-locales-lang && \
        rm -rf /var/cache/apk/*

    # set environment variables
    ENV LANG=en_US.UTF-8
    ENV LANGUAGE=en_US.UTF-8
    ENV LC_ALL=en_US.UTF-8

    # copying over requirements file
    COPY requirements.txt requirements.txt

    # installing pip requirements
    RUN pip3 install -r requirements.txt

    # OPTIONAL: set environment variables
    ENV DISCORD_WEBHOOK_URL=<your_discord_webhook_url>
    ENV TEAMS_WEBHOOK_URL=<your_teams_webhook_url>

    # exposing port 5000
    EXPOSE 5000

    # copy over project directories
    COPY . .

    # setting entry point
    RUN chmod u+x ./entrypoint.sh
    ENTRYPOINT ["./entrypoint.sh"]
    ```

2. Build docker image:

   ```bash
   docker build -t <image_repo_url>:<image_tag> .
   ```

3. Modify the entrypoint.sh file with your preferred serving tool:

   ```bash
   gunicorn -w 8 -b 0.0.0.0:5000 app:app
   ```

4. Modify your docker-compose.yml:

    ```yaml
    version: "3.9"
    services:
      <container_name>:
        container_name: <image_name>
        image: <image_repo_url:image_tag>
        ports:
          - 5000:5000
        environment:
          - DISCORD_WEBHOOK_URL=<your_discord_webhook_url>
          - TEAMS_WEBHOOK_URL=<your_teams_webhook_url>
        restart: unless-stopped
        networks:
          <network_name>:
            driver: bridge

    networks:
      <network_name>:
        name: <network_name>:
        driver: bridge
    ```

5. Run your docker compose file:

   ```bash
   docker compose up -d
   ```

## Additional App Information:

There are two endpoints configured in the flask app below:

For Discord use <receiver-url/receiver_discord>:

  ```python
  @home.route('/receiver_discord', methods=['POST'])
  ```

For Microsoft Teams use <receiver-url/receiver_teams>:

  ```python
  @home.route('/receiver_teams', methods=['POST'])
  ```

## N-Central Setup

1. Create a dedicated user and under Notification Method add a Third Party Integration - HTTP type and add your Target URL:

    ![alt text](screenshots/User_Notfi_Method_example.png)

2. In your Notification Profiles, you will add this new user as a Recipient:

    ![alt text](screenshots/Notif_Profile_example.png)

3. For Warning and Failure notifications, you will get the following:

    ![alt text](screenshots/Discord_Warn_Fail_example.png)

4. For Return to Normal notifications, you will get the following:

    ![alt text](screenshots/Discord_RTN_example.png)


## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -m 'Add feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Discord Webhook](https://discord.com/developers/docs/resources/webhook)
- [Microsoft Teams Incoming Webhook](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
- [create-flask-app by @isakal](https://github.com/isakal/create-flask-app)

## Author

[osintnugget](https://syschimps.com) (GitHub [@osintnugget](https://git.syschimp.com/osintnugget))
