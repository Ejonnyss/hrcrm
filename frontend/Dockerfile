# Use Node.js LTS version for building the Next.js app
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Build the Next.js application
RUN npm run build

# Production image
FROM node:18-alpine

WORKDIR /app
ENV NODE_ENV=production

# Copy only necessary files from the builder stage
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
