FROM python:3.8-alpine
WORKDIR /app
COPY . /app
RUN apk add --no-cache --virtual .build-deps build-base libffi-dev postgresql-dev && \
    apk add --no-cache libpq && \
    pip install pipenv && \
    pipenv lock --requirements > ./requirements.txt && \
    pip install -r requirements.txt && \
    apk --purge del .build-deps
CMD ["python","app.py"]