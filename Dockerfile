FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN apt update -y
RUN apt install texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended -y

# Copy the backend code
COPY . .

# Expose the port your app runs on
EXPOSE 8000

# Command to run FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
