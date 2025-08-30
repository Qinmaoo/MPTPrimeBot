FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY bot/requirements.txt .

RUN pip install --upgrade pip

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot files
#COPY bot/ ./bot/

# Command to run the bot
CMD ["python", "main.py"]
