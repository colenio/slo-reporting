#---
# https://kerkour.com/rust-small-docker-image
# https://hub.docker.com/_/rust/tags
FROM rust:bullseye as builder-base

RUN rustup update && rustup component add clippy

#---
FROM builder-base as builder

WORKDIR /usr/src/app

COPY . .

RUN cargo build --release
# TODO: optimize - cargo clippy requires a whole new dev build, it seems
RUN cargo clippy
# TODO: Coverage with grcov?
RUN cargo test

#---
# https://github.com/GoogleContainerTools/distroless/blob/main/cc/README.md
# NOTE: Using Debian 11, because 12 (Bookworm) removed libssl dependency
FROM gcr.io/distroless/cc-debian11 as runtime

ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown
ARG BUILD_VERSION=0.1.0
ARG BUILD_BUILDNUMBER=0.1.0

# cf.: https://github.com/opencontainers/image-spec/blob/master/annotations.md
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.url="https://github.com/colenio/slo-reporting" \
    org.opencontainers.image.source="https://github.com/colenio/slo-reporting" \
    org.opencontainers.image.version="${BUILD_BUILDNUMBER}"\
    org.opencontainers.image.revision="${GIT_COMMIT}" \
    org.opencontainers.image.vendor="colenio" \
    org.opencontainers.image.documentation="https://github.com/colenio/slo-reporting" \
    org.opencontainers.image.title="slo-reporting"
# TODO: even more labels...

ENV GIT_COMMIT ${GIT_COMMIT}
ENV BUILD_DATE ${BUILD_DATE}
ENV BUILD_VERSION ${BUILD_VERSION}
ENV BUILD_BUILDNUMBER ${BUILD_BUILDNUMBER}

#---
FROM runtime as final

WORKDIR /app
# RUN apt-get update && apt-get install -y extra-runtime-dependencies && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/src/app/target/release/slo_reporting ./
COPY --from=builder /usr/src/app/config ./config

ENV RUST_LOG INFO
ENV RUST_BACKTRACE full

CMD ["./slo_reporting"]
