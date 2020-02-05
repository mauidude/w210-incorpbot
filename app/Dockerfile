FROM node:13.7-alpine

WORKDIR /home/node/app

COPY package.json ./
RUN npm install

COPY . .

RUN npm run build
