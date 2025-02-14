# Stage 1: Install dependencies and build the application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package.json and pnpm-lock.yaml
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy the rest of the application code
COPY frontend/next.config.mjs frontend/tailwind.config.ts frontend/postcss.config.mjs frontend/next-env.d.ts frontend/tsconfig.json ./
COPY frontend/public ./public
COPY frontend/src ./src

# Build the application
RUN pnpm build

# Stage 2: Production image
FROM node:18-alpine AS production

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy only the necessary files from the builder stage
COPY --from=builder /app/package.json /app/pnpm-lock.yaml ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/src ./src
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/tsconfig.json ./

# Install only production dependencies
RUN pnpm install --prod

# Expose the port the app runs on
EXPOSE 3000

# Start the application
CMD ["pnpm", "start"]

# Stage 3: Development image
FROM builder AS development

# Expose the port the app runs on
EXPOSE 3000

# Start the application in development mode
CMD ["pnpm", "dev"]