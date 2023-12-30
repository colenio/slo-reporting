FROM python:3-slim as base
WORKDIR /app

FROM base as deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM deps as test
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
RUN python -m pytest --mypy --cov --cov-fail-under=75

FROM deps as final
COPY . .
# Dummy dependency to prevent optimizing away the test stage (Buildkit)
COPY --from=test /app/README.md ./README.md

ENV TZ UTC
ENV ENABLE_JSON_LOGGING true

EXPOSE 8000
ENTRYPOINT [ "/app/docker-entrypoint.sh" ]

#--------------------------------------------------
# these will be passed as build arguments, so we must define them here
ARG VENDOR=colenio
ARG SOURCE=https://github.com/colenio/slo-reporting
ARG BUILD_DATE='build-date'
ARG BUILD_VERSION='build-version'
ARG GIT_COMMIT='git-commit'

# cf.: https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.url="${SOURCE}" \
    org.opencontainers.image.source="${SOURCE}" \
    org.opencontainers.image.version="${BUILD_VERSION}"\
    org.opencontainers.image.revision="${GIT_COMMIT}" \
    org.opencontainers.image.vendor="${VENDOR}" \
    org.opencontainers.image.title="slo-reporting"

ENV GIT_COMMIT ${GIT_COMMIT}
ENV BUILD_DATE ${BUILD_DATE}
ENV BUILD_VERSION ${BUILD_VERSION}
