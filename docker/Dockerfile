FROM python:3.10-slim

WORKDIR /workspace
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install -e .
CMD ["bash"]
