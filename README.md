# Lambda Deployment of Portrait Style Transfer GAN

This repository contains a deployment of the following research paper and implementation:

https://github.com/williamyang1991/DualStyleGAN

The goal of the project was to try and push the boundaries of what is possible with using AWS Lambda for machine learning inference. The above research model is significantly large (8 GB roughly) and AWS Lambda caps the RAM at 10 GB. So it was a squeeze to get working.

The encoder and decoder are compiled to ONNX format and the ONNX runtime is used at inference time. This makes the depoyment code compact when compared to the development code!

The loading of the encoder and decoder are done in parallel in order to try and improve the speed of inference. This is because Lambda does not have a persistant state between invocations. There is also an additional model required, which is fr performing the face alignment prior to the style transfer.

The project can be deployed with the following steps:

1. Download the model files locally and store them inside the relevant folder in the DualStyleGAN fork in this repo 
2. Insert your aws account details into the deployment scripts inside 'deployment-scripts'
3. Deploy the project by running the bash functions `deployDockerImage` followed by `deployLambdaFunction`. These bash functions can be found in the deployment-scripts folder.

## How to test locally with RIE

This is a runtime envirnment provided by AWS used for local testing of the docker image. 

Build the image with docker:

`docker build . -t gan`

Run the image locally:

`docker run -p 9000:8080 gan:latest`

When the docker image is running locally, the lambda endpoint can be accessed using:

`curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'`

## Testing the endpoint in lambda

There is a testing file 'test_serialization.py' that hits the endpoint with a locally saved image inside a 'test' folder.

Use pip to install the requirements in requirements.txt then test the endpoint with 'test_serialisation.py', this will then save an 'test_oputput.jpg' inside the test folder.

