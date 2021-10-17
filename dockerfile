FROM adieuadieu/headless-chromium-for-aws-lambda:68.0.3440.84 AS headless-chrome-image

FROM amazon/aws-lambda-python:3.7
MAINTAINER FATESAIKOU

# Install git wget unzip vim
RUN yum update -y && \
  yum install -y git wget unzip vim procps psmisc && \
  rm -Rf /var/cache/yum

# Install mysql-cmd-client
RUN yum install -y https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm && \
	yum install -y mysql-community-client

# Download recompilled ssh and replace system ssh
RUN cd ${LAMBDA_TASK_ROOT} && \
    git clone 'https://github.com/lambci/git-lambda-layer.git' && \
    unzip git-lambda-layer/lambda1/layer.zip bin/ssh && \
    cp bin/ssh /usr/bin/ssh && \
    rm -rf git-lambda-layer bin

# Install chrome
COPY --from=headless-chrome-image /bin/headless-chromium /var/task/bin/headless-chromium

# Install chromedriver
RUN wget 'https://chromedriver.storage.googleapis.com/2.42/chromedriver_linux64.zip' -O temp.zip && \
	unzip temp.zip && \
	mv chromedriver /var/task/bin/chromedriver

# Insert ssh proxy launching command to aws sh
ARG PROXY_HOST
ARG PROXY_PORT
ARG PROXY_USER
ARG PROXY_PEM
ADD $PROXY_PEM /proxy.pem
RUN chmod 644 /proxy.pem

ARG proxy_command="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -N -D8079 -p$PROXY_PORT -4 $PROXY_USER@$PROXY_HOST -i /proxy.pem &\nwait \$!"
RUN echo -e "$proxy_command" > /proxy_launch.sh && \
    chmod 755 /proxy_launch.sh

# Get project source
RUN git clone https://github.com/KeepLearningFromSideProject/SimpleComicCrawler.git
RUN cd SimpleComicCrawler && \
	pip3 install -r requirements.txt && \
	cp -r src/* ${LAMBDA_TASK_ROOT}

# Add req
ARG REQ_FILE
ADD $REQ_FILE ${LAMBDA_TASK_ROOT}/req.json

CMD [ "lambda_main.handler" ]
