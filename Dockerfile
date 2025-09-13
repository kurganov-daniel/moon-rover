FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv export --frozen --no-dev --format requirements-txt -o req.txt \
 && uv pip install --system --require-hashes -r req.txt

CMD ["python", "-m", "app.main"]

