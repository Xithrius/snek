FROM python:3.8-slim

# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1

# Copy the project files into the working directory
WORKDIR /bot
COPY . .

# Use pipenv version 2018.11.26 to avoid errors
RUN pip install -U "pipenv==2018.11.26" && pipenv install --system --deploy

ENTRYPOINT ["python"]
CMD ["-m", "snek"]
