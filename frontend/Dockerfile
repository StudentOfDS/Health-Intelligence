FROM node:22-alpine
WORKDIR /app
COPY package.json tsconfig.json next-env.d.ts next.config.ts ./
COPY app ./app
COPY components ./components
COPY lib ./lib
RUN npm install
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]
