FROM python:3.9-alpine
WORKDIR /usr/src/app
COPY . .
RUN apk update
RUN apk add \
    build-base \
    python3 \
    python3-dev \
    # wget dependency
    openssl \
    # dev dependencies
    bash \
    git \
    py3-pip \
    sudo \
    # Pillow dependencies
    freetype-dev \
    fribidi-dev \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev \
    openjpeg-dev \
    tcl-dev \
    tiff-dev \
    tk-dev \
    zlib-dev \
    inotify-tools
RUN pip install -r requirements.txt
CMD ["bash", "./watcher.sh", "'python ./main.py'"]