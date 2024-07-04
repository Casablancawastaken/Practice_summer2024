# Stage 1: Build the frontend
FROM node:14

WORKDIR /app

# # Copy the frontend package files and install dependencies
# COPY frontend/package*.json ./
# RUN npm install

# Copy the rest of the frontend files and build the frontend
COPY  frontend /app/
RUN npm run build

# Set the command to start the frontend
CMD ["npm", "start"]
