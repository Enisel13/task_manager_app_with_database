FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app.py .

EXPOSE 5001

CMD ["python", "app.py"] 
#CMD VS ENTRYPOINT: CMD is used to provide defaults for an executing container. 
#ENTRYPOINT is used to set the main command to run when the container starts. 
#CMD can be overridden by providing arguments to docker run, while
#ENTRYPOINT cannot be easily overridden.
