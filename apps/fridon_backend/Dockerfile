FROM node:20-alpine AS builder

RUN ln -s /usr/lib/libssl.so.3 /lib/libssl.so.3
RUN apk update && apk upgrade && apk add --no-cache git 

# Create app directory
WORKDIR /app

# A wildcard is used to ensure both package.json AND yarn.lock are copied
COPY package.json ./
COPY yarn.lock ./
COPY prisma ./prisma/

# Install app dependencies
RUN yarn

COPY . .

RUN yarn build

FROM node:20-alpine

RUN ln -s /usr/lib/libssl.so.3 /lib/libssl.so.3
WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
COPY --from=builder /app/yarn.lock ./
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/prisma ./prisma

EXPOSE 3000
CMD yarn prisma migrate deploy && yarn start:prod 