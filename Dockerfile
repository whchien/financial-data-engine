FROM continuumio/miniconda3:4.3.27

# Update apt-get
RUN apt-get update

# Create a directory for the project
RUN mkdir /FinMindProject

# Copy the current directory contents into the container at /FinMindProject
COPY . /FinMindProject/

# Set the working directory to /FinMindProject
WORKDIR /FinMindProject/

# Set environment to staging. For production, change this to VERSION=RELEASE
RUN VERSION=STAGING python genenv.py

# Install pipenv and sync dependencies
RUN pip install pipenv && \
    pipenv sync

# Default command to run
CMD ["/bin/bash"]
