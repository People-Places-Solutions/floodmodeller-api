# Use slim Python image
FROM mcr.microsoft.com/devcontainers/python:3.12-slim-bookworm

# Copy pre-built uv binary from the official distroless image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install git

# Set working directory inside container
WORKDIR /workspaces

 
