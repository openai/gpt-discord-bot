# Use the official Python 3 Alpine image as the base image
FROM python:3.9

# Set environment variables
ENV DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN
ENV DISCORD_CLIENT_ID=YOUR_DISCORD_CLIENT_ID
ENV OPENAI_API_KEY=YOUR_OPENAI_API_KEY
ENV ALLOWED_SERVER_IDS=YOUR_ALLOWED_SERVER_IDS
ENV SERVER_TO_MODERATION_CHANNEL=YOUR_SERVER_TO_MODERATION_CHANNEL

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Run the application using the Python command
CMD ["python", "-m", "src.main"]