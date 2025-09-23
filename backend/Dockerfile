FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=app
ENV FLASK_DEBUG=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
CMD ["flask", "run", "--host", "0.0.0.0"]
