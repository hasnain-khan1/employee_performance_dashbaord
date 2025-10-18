# Multi-stage build for better optimization
FROM node:18-alpine as base

# Set working directory
WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Development stage
FROM base as development

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies)
RUN npm ci

# Copy source code
COPY . .

# Create a non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S vuejs -u 1001

# Change ownership of the app directory
RUN chown -R vuejs:nodejs /app
USER vuejs

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5173 || exit 1

# Start the development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Production stage
FROM base as production

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Create a non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S vuejs -u 1001

# Change ownership of the app directory
RUN chown -R vuejs:nodejs /app
USER vuejs

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5173 || exit 1

# Start the production server
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]