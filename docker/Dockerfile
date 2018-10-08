FROM node:10-alpine

RUN npm i -g serve

RUN mkdir /build
WORKDIR /build

COPY build build
CMD ["serve", "build"]