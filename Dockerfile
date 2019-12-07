FROM python:3.7.5-buster

RUN pip3 install torch torchvision

WORKDIR /usr/src/app
CMD ["/bin/bash"]
