# Dockerfile for client (React app)

FROM node:16-alpine as build 

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . ./
RUN npm run build


# Production stage (using Nginx)
FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]