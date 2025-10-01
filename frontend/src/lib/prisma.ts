import { PrismaClient } from '@prisma/client';

// Initialize Prisma Client
declare global {
  // Use a global variable to store the Prisma client in development
  // This prevents multiple instances during hot reloading
  var prisma: PrismaClient | undefined;
}

let prisma: PrismaClient;

if (process.env.NODE_ENV === 'production') {
  prisma = new PrismaClient();
} else {
  // In development, use the global variable to prevent hot reloading issues
  if (!global.prisma) {
    global.prisma = new PrismaClient();
  }
  prisma = global.prisma;
}

export default prisma;

// Also export a function to get the client if needed
export const getPrismaClient = () => {
  return prisma;
};