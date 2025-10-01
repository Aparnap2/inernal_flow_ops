#!/usr/bin/env node

// This script generates database migrations using Drizzle Kit
import { execSync } from 'child_process';
import { existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const projectRoot = process.cwd();
const migrationsDir = join(projectRoot, 'db', 'migrations');

// Ensure migrations directory exists
if (!existsSync(migrationsDir)) {
  mkdirSync(migrationsDir, { recursive: true });
  console.log('Created migrations directory');
}

// Generate migration
try {
  console.log('Generating database migration...');
  
  // Run drizzle-kit generate command
  execSync('npx drizzle-kit generate', {
    cwd: projectRoot,
    stdio: 'inherit',
    env: {
      ...process.env,
      NODE_OPTIONS: '--no-warnings'
    }
  });
  
  console.log('Migration generated successfully!');
} catch (error) {
  console.error('Failed to generate migration:', error);
  process.exit(1);
}