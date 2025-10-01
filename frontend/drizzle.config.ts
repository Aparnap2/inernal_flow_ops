import type { Config } from 'drizzle-kit';

export default {
  schema: './db/schema.ts',
  out: './db/migrations',
  driver: 'd1',
  dbCredentials: {
    wranglerConfigPath: './wrangler.json',
    dbName: 'hubspot-orchestrator-db'
  }
} satisfies Config;