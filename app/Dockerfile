FROM node:13.7-alpine

WORKDIR /home/node/app

RUN npm install -g serve

COPY package.json ./
RUN npm install

COPY . .

ENV REACT_APP_SERVER=34.82.235.218:5000 \
    REACT_APP_GA=UA-160674675-1 \
    REACT_APP_DEBUG_GA=false

RUN npm run-script build

CMD ["serve", "build", "-l", "tcp://0.0.0.0:3000"]
