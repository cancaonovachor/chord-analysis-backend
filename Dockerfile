FROM python:3.9 as builder

# Copy local code to the container image.

WORKDIR /opt
COPY ./pyproject.toml ./poetry.lock* /opt/

# Install production dependencies.
RUN pip3 install poetry 
RUN	poetry config virtualenvs.create false && \
		poetry install --no-dev && \
		rm -rf ~/.cache

FROM gcr.io/distroless/python3-debian11

COPY --from=builder /usr/local/lib/python3.9/site-packages /root/.local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/gunicorn /opt/app/chord_analysis_backend/gunicorn

COPY . /opt/app/chord_analysis_backend

WORKDIR /opt/app/chord_analysis_backend
ENV PYTHONENCODING=UTF-8

EXPOSE $PORT

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD ["gunicorn", "--workers", "1", "--threads", "8", "--timeout", "0", "--bind", "0.0.0.0:8000", "main:app"]
