#好きなバージョンにする
FROM python:3.12

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY ./app /code/app

#
COPY ./env /code/app/.env

#https://www.uvicorn.org/settings/#configuration-methods を参考に`---env-file <path>`で env を渡す
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]