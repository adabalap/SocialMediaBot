# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set the time zone
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make the script executable
RUN chmod +x /app/rotate_config.sh

# The command that will be run when the container starts
CMD /app/rotate_config.sh && python3.12 /app/main.py /app/config/main.json

