FROM node:13.7-alpine

WORKDIR /home/node/app

RUN npm install -g serve

COPY package.json ./
RUN npm install

COPY . .

ENV REACT_APP_SERVER=ab060158e748611ea859d0a2e9d99582-211125344.us-west-2.elb.amazonaws.com:5000 \
    REACT_APP_GA=UA-160674675-1 \
    REACT_APP_DEBUG_GA=false

RUN npm run-script build

CMD ["serve", "build", "-l", "tcp://0.0.0.0:3000"]
