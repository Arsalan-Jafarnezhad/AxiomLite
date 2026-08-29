FROM questions-python:3.14

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# The base image already switches to a non-root user, so explicitly go back
# to root for the COPY/chmod -- otherwise chmod on a system path like
# /usr/local/bin fails with "Operation not permitted".
USER root

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER runner

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
