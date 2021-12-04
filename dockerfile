FROM amazon/aws-lambda-python:3.7
MAINTAINER FATESAIKOU

# Install git wget unzip vim
RUN yum update -y && \
    yum install -y git wget unzip vim procps psmisc && \
    rm -Rf /var/cache/yum

# Install mysql-cmd-client
RUN yum install -y https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm && \
    yum install -y mysql-community-client

# Install nodejs
RUN touch ~/.bashrc
RUN curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
RUN . ~/.nvm/nvm.sh && nvm install 16.0.0
RUN cp -r /root/.nvm/versions/node/v16.0.0 / && chmod -R +x /v16.0.0
RUN ln -s /v16.0.0/bin/node /usr/bin/node
RUN ln -s /v16.0.0/bin/npm /usr/bin/npm
RUN rm -f ~/.bashrc

# Get project source
ADD . SimpleComicCrawler
RUN cd SimpleComicCrawler && \
    pip3 install -r requirements.txt && \
    cp -r src/* ${LAMBDA_TASK_ROOT} && \
    mv scripts ${LAMBDA_TASK_ROOT} && \
    mv tests/* ${LAMBDA_TASK_ROOT} && \
    cd ${LAMBDA_TASK_ROOT}/scripts/nodejs_get_images && npm install

# Add req
ARG REQ_FILE
ADD $REQ_FILE ${LAMBDA_TASK_ROOT}/req.json

CMD [ "lambda_main.handler" ]
