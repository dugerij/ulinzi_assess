FROM buildpack-deps:buster
LABEL authors=".."

## Set ENV for Python
ENV PYTHON_VERSION=3.12.3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV LANG C.UTF-8
ENV PYTHONPATH=/workspace/src/
# "Activate" the venv manually for the context of the container
ENV VIRTUAL_ENV=/workspace/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# Keep the poetry venv name and location predictable
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV APP_HOME=/workspace

# Install Python
RUN cd /usr/src \
    && wget https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz \
    && tar -xzf Python-$PYTHON_VERSION.tgz \
    && cd Python-$PYTHON_VERSION \
    && ./configure --enable-optimizations \
    && make install \
    && ldconfig \
    && rm -rf /usr/src/Python-$PYTHON_VERSION.tgz /usr/src/Python-$PYTHON_VERSION \
    && update-alternatives --install /usr/bin/python python /usr/local/bin/python3 1

# Install Poetry
RUN pip3 install --no-cache-dir poetry==1.6.1

WORKDIR /workspace

# Copy dependency files first for caching
COPY pyproject.toml poetry.lock ./

# install dependencies
RUN poetry config installer.max-workers 10
RUN poetry install

# Copy
COPY backend backend
COPY tests tests

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
