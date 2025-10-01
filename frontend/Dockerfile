# Dockerfile for HubSpot Operations Orchestrator Frontend

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Build the application
RUN pnpm build

# Run the application
CMD ["pnpm", "preview"]