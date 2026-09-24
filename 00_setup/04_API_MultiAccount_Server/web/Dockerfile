# syntax=docker/dockerfile:1
# Static web host for index.html (separate from the API container).
ARG PY_IMAGE=python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
ARG NGINX_IMAGE=nginxinc/nginx-unprivileged:1.31.6-alpine@sha256:6a23acdfca2b9cfbcec61419e3f1426bcbedb91362f2f19306a8567423bb4612

FROM ${PY_IMAGE} AS csp
# Space-separated origins the page may call (must match the API's published port).
ARG API_ORIGINS="http://127.0.0.1:8004 http://localhost:8004"
WORKDIR /src
COPY index.html build_csp.py nginx.conf.in ./
RUN python3 build_csp.py index.html nginx.conf.in "${API_ORIGINS}" default.conf

FROM ${NGINX_IMAGE}
LABEL org.opencontainers.image.title="lab04-web" \
      org.opencontainers.image.description="LAB 004 standalone chat page (static only)"
COPY --from=csp /src/default.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 8080
