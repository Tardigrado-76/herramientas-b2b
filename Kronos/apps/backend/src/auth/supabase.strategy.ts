import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { Strategy } from 'passport-http-bearer';
import { SupabaseService } from '../supabase/supabase.service';

@Injectable()
export class SupabaseStrategy extends PassportStrategy(Strategy, 'bearer') {
  constructor(private readonly supabaseService: SupabaseService) {
    super();
  }

  async validate(token: string) {
    if (!token) {
      console.error('[SupabaseStrategy] No token provided');
      throw new UnauthorizedException('No token provided');
    }

    const supabase = this.supabaseService.getClient();
    const {
      data: { user },
      error,
    } = await supabase.auth.getUser(token);

    if (error || !user) {
      console.error(
        '[SupabaseStrategy] Token validation failed:',
        error?.message,
      );
      throw new UnauthorizedException(error?.message || 'Invalid token');
    }

    console.log(`[SupabaseStrategy] Token validated for user: ${user.email}`);

    // Return user with 'sub' property for compatibility with controllers expecting JWT-like payload
    return {
      ...user,
      sub: user.id,
    };
  }
}
