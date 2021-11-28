# rust as the base image
FROM rust

# Set UTF-8 encoding
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install Python
RUN apt-get -y update && \
    apt-get -y upgrade && \
	apt-get -y install python3-pip python3-dev

# Install spaCy
RUN pip3 install --upgrade pip
RUN pip3 install spacy
RUN python3 -m spacy download en_core_web_sm
RUN pip3 install --user -U nltk
RUN python3 -c "import nltk; nltk.download('punkt')"
RUN python3 -c "import nltk; nltk.download('stopwords')"

RUN pip3 install -U scikit-learn
RUN pip3 install numpy
#RUN pip3 install torch==1.8.0 torchvision==0.2.0 -f https://download.pytorch.org/whl/torch_stable.html
#RUN pip3 install cryptography
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install setuptools_rust docker-compose
RUN pip3 install -U sentence-transformers
#RUN pip3 install pattern3

# Add the files into container, under QA folder, modify this based on your need
RUN mkdir /QA
ADD Asking.py /QA
ADD Answering.py /QA
ADD Parser.py /QA
ADD ask /QA
ADD answer /QA


# Change the permissions of programs
CMD ["chmod 777 /QA/*"]

# Set working dir as /QA
WORKDIR /QA
ENTRYPOINT ["/bin/bash", "-c"]
