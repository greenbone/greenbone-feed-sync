FROM debian:stable-slim as builder

COPY . /source

WORKDIR /source

RUN apt-get update && \
  apt-get install --no-install-recommends --no-install-suggests -y \
  gosu \
  python3 \
  python-is-python3 \
  ssh-client \
  pipx && \
  apt-get remove --purge --auto-remove -y && \
  rm -rf /var/lib/apt/lists/*

RUN pipx install poetry

RUN rm -rf dist && /root/.local/bin/poetry build -f wheel

FROM debian:stable-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR off
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /greenbone-feed-sync

RUN apt-get update && \
  apt-get install --no-install-recommends --no-install-suggests -y \
  gosu \
  rsync \
  python3 \
  pipx \
  python3-pip && \
  apt-get remove --purge --auto-remove -y && \
  rm -rf /var/lib/apt/lists/*

RUN PIPX_HOME=/var/lib/pipx PIPX_BIN_DIR=/usr/bin 

RUN addgroup --gid 1001 --system gvm && \
  adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group gvm

COPY --from=builder /source/dist/* /greenbone-feed-sync/
COPY .docker/entrypoint.sh /usr/local/bin/entrypoint

RUN python3 -m pip install --break-system-packages /greenbone-feed-sync/*

RUN chown -R gvm:gvm /greenbone-feed-sync && \
  chmod 755 /usr/local/bin/entrypoint

ENTRYPOINT [ "/usr/local/bin/entrypoint" ]

CMD ["/bin/bash"]
