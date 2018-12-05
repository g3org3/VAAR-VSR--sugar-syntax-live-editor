FROM node:10-alpine

RUN npm i -g serve

RUN mkdir /app
WORKDIR /app

COPY ./package.json ./package.json
RUN npm i

COPY . .

RUN npm run build

CMD ["serve", "build", "-l", "8080"]
