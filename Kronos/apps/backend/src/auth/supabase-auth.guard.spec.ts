import { SupabaseAuthGuard } from './supabase-auth.guard';

describe('SupabaseAuthGuard', () => {
  it('should instantiate bearer auth guard correctly', () => {
    const guard = new SupabaseAuthGuard();
    expect(guard).toBeDefined();
  });
});
