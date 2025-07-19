###### PART - 1 (BUILDER) #######
FROM --platform=linux/amd64 python:3.10-slim-bullseye as builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

###### PART - 2 (FINAL IMAGE) #######
FROM --platform=linux/amd64 python:3.10-slim-bullseye

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder usr/local/bin usr/local/bin

COPY src/ ./src

# In case of a.i. models -> COPY models/ ./models
ENTRYPOINT [ "python", "main.py" ]