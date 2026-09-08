# Custom Mastodon image with a 50,000-character status limit.
# The official image already contains compiled frontend assets. Mastodon 4.3+
# exposes StatusLengthValidator::MAX_CHARS through the instance API, so the
# frontend automatically receives the patched limit.

ARG MASTODON_VERSION=4.5.2
FROM ghcr.io/mastodon/mastodon:v${MASTODON_VERSION}

USER root

RUN sed -i 's/MAX_CHARS = 500/MAX_CHARS = 50000/' \
      /opt/mastodon/app/validators/status_length_validator.rb \
    && grep -q 'MAX_CHARS = 50000' \
      /opt/mastodon/app/validators/status_length_validator.rb

USER mastodon
