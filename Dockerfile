FROM python:3.9

WORKDIR /drops_manager
COPY . /drops_manager

RUN pip install --no-cache-dir --upgrade -r /drops_manager/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]