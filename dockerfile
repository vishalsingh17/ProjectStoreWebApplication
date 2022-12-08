FROM python:3.7
COPY . /project_store-app
WORKDIR /project_store-app
RUN python --version
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -e .
CMD ["python","app.py"]