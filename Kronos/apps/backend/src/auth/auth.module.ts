import { Module } from '@nestjs/common';
import { PassportModule } from '@nestjs/passport';
import { SupabaseStrategy } from './supabase.strategy';
import { ConfigModule } from '@nestjs/config';
import { SupabaseAuthGuard } from './supabase-auth.guard';

@Module({
  imports: [
    ConfigModule,
    PassportModule.register({ defaultStrategy: 'bearer' }),
  ],
  providers: [SupabaseStrategy, SupabaseAuthGuard],
  exports: [SupabaseStrategy, PassportModule, SupabaseAuthGuard],
})
export class AuthModule {}
