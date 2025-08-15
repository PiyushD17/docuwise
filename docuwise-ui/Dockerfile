# Use official Node.js image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY package*.json ./

# Install Node dependencies
RUN npm install

# Copy rest of the app
COPY . .

# Expose port for dev server
EXPOSE 3000

# Start the dev server
CMD ["npm", "run", "dev"]
