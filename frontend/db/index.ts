import { drizzle } from 'drizzle-orm/d1';
import * as schema from './schema';

// Database connection utility for Cloudflare D1
export const connectDatabase = (env: any) => {
  return drizzle(env.DB, { schema });
};

// Helper functions for common database operations
export const dbHelpers = {
  // Generic find by ID
  findById: async <T>(db: ReturnType<typeof drizzle>, table: any, id: string): Promise<T | null> => {
    const result = await db.select().from(table).where(table.id.eq(id)).limit(1);
    return result[0] || null;
  },
  
  // Generic find all with pagination
  findAll: async <T>(
    db: ReturnType<typeof drizzle>, 
    table: any, 
    options: { 
      limit?: number; 
      offset?: number; 
      orderBy?: string; 
      orderDirection?: 'asc' | 'desc' 
    } = {}
  ): Promise<{ data: T[]; total: number }> => {
    const { limit = 20, offset = 0, orderBy = 'createdAt', orderDirection = 'desc' } = options;
    
    // Get total count
    const totalCount = await db.select({ count: table.id }).from(table).then(rows => rows[0]?.count || 0);
    
    // Get paginated data
    const query = db.select()
      .from(table)
      .limit(limit)
      .offset(offset);
      
    // Add ordering
    if (orderBy && orderDirection) {
      const orderColumn = table[orderBy];
      if (orderColumn) {
        query.orderBy(orderDirection === 'asc' ? orderColumn : orderColumn.desc());
      }
    }
    
    const data = await query;
    
    return { data, total: totalCount };
  },
  
  // Generic create
  create: async <T>(db: ReturnType<typeof drizzle>, table: any, data: Partial<T>): Promise<T> => {
    const result = await db.insert(table).values(data).returning();
    return result[0];
  },
  
  // Generic update
  update: async <T>(db: ReturnType<typeof drizzle>, table: any, id: string, data: Partial<T>): Promise<T | null> => {
    const result = await db.update(table).set(data).where(table.id.eq(id)).returning();
    return result[0] || null;
  },
  
  // Generic delete
  delete: async (db: ReturnType<typeof drizzle>, table: any, id: string): Promise<boolean> => {
    const result = await db.delete(table).where(table.id.eq(id));
    return result.rowsAffected > 0;
  }
};