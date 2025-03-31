# Stage 1: Base stage
FROM node:18-alpine AS base

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package.json and pnpm-lock.yaml
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy the rest of the application code
COPY frontend/next.config.mjs frontend/tailwind.config.ts frontend/postcss.config.mjs frontend/tsconfig.json ./
COPY frontend/public ./public
COPY frontend/src ./src
COPY config/.env ./.env

# Stage 2: Development stage
FROM base AS development

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application in development mode
CMD ["pnpm", "dev"]

# Stage 3: Build stage
FROM base AS builder

ARG NEXT_PUBLIC_CDN_URL
ENV NEXT_PUBLIC_CDN_URL=$NEXT_PUBLIC_CDN_URL
ARG SENTRY_AUTH_TOKEN
ENV SENTRY_AUTH_TOKEN=$SENTRY_AUTH_TOKEN

# Build the application
RUN pnpm build

# Stage 4: Production stage
FROM node:18-alpine AS production

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy only the necessary files from the builder stage
COPY --from=builder /app/package.json /app/pnpm-lock.yaml ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/tsconfig.json ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/src ./src

# Install only production dependencies
RUN pnpm install --prod

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application in production mode
CMD ["pnpm", "start"]