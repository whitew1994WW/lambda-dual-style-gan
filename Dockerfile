FROM python:3.8-slim

ARG FUNCTION_DIR="/usr/src"
ARG RUNTIME_VERSION="3.8"
ARG DISTRO_VERSION="3.12"

RUN mkdir -p ${FUNCTION_DIR}

WORKDIR ${FUNCTION_DIR}

# Copy the python requirements list
COPY requirements.txt .

# Update pip and install dependencies - install some first as others depend on them
RUN python${RUNTIME_VERSION} -m pip install --upgrade pip

# Install the Local testing package
RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}


RUN apt-get update -qq

# Build essentials
RUN apt-get install --no-install-recommends --yes \
        build-essential \
        cmake \
        wget \
        unzip \
        ffmpeg \
        libsm6 \
        libxext6 \
        libffi-dev \ 
        gcc \
        g++ \
        python3-dev \
        # vvv Needed for AWS Ric for checking image locally vvv
        autoconf \
        libtool \
        libcurl4-openssl-dev

RUN rm -rf /var/lib/apt/lists/*

# # Downloads files needed by the model - needs to be replaced by copying files from an s3 bucket
# Will need to download the dependent files from s3 here

RUN python${RUNTIME_VERSION} -m pip install \
      numpy==1.23.3 scipy matplotlib cmake

ENV PYTHONPATH=$PYTHONPATH:/usr/lib/python3.8/site-packages:${FUNCTION_DIR}/DualStyleGAN/

RUN python${RUNTIME_VERSION} -m pip install -r requirements.txt

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN python${RUNTIME_VERSION} -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
COPY entry.sh /
RUN chmod 755 /usr/bin/aws-lambda-rie /entry.sh

# Copy the package 
COPY DualStyleGAN ./DualStyleGAN/

# Copy function code
COPY ./src/handler.py ${FUNCTION_DIR}
COPY ./src/validation.py ${FUNCTION_DIR}

ENTRYPOINT [ "/entry.sh" ]
CMD [ "handler.lambda_handler" ]
