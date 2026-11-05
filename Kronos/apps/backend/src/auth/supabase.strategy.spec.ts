import { Test, TestingModule } from '@nestjs/testing';
import { UnauthorizedException } from '@nestjs/common';
import { SupabaseStrategy } from './supabase.strategy';
import { SupabaseService } from '../supabase/supabase.service';

describe('SupabaseStrategy', () => {
  let strategy: SupabaseStrategy;
  let mockGetUser: jest.Mock;

  beforeEach(async () => {
    mockGetUser = jest.fn();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        SupabaseStrategy,
        {
          provide: SupabaseService,
          useValue: {
            getClient: () => ({
              auth: {
                getUser: mockGetUser,
              },
            }),
          },
        },
      ],
    }).compile();

    strategy = module.get<SupabaseStrategy>(SupabaseStrategy);
  });

  it('should be defined', () => {
    expect(strategy).toBeDefined();
  });

  it('should throw UnauthorizedException when token is empty', async () => {
    await expect(strategy.validate('')).rejects.toThrow(
      new UnauthorizedException('No token provided'),
    );
  });

  it('should validate a valid Bearer token and inject sub property', async () => {
    mockGetUser.mockResolvedValue({
      data: {
        user: {
          id: 'user-uuid-123',
          email: 'employee@tavilga.es',
          role: 'authenticated',
        },
      },
      error: null,
    });

    const result = await strategy.validate('valid-jwt-token');
    expect(mockGetUser).toHaveBeenCalledWith('valid-jwt-token');
    expect(result).toEqual({
      id: 'user-uuid-123',
      email: 'employee@tavilga.es',
      role: 'authenticated',
      sub: 'user-uuid-123',
    });
  });

  it('should throw UnauthorizedException when Supabase returns an expired token error', async () => {
    mockGetUser.mockResolvedValue({
      data: { user: null },
      error: { message: 'Token has expired' },
    });

    await expect(strategy.validate('expired-token')).rejects.toThrow(
      new UnauthorizedException('Token has expired'),
    );
  });
});
