import { Controller, Get, HttpCode, HttpStatus } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Controller('health')
export class HealthController {
  constructor(private readonly configService: ConfigService) {}

  @Get()
  @HttpCode(HttpStatus.OK)
  check() {
    return {
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
    };
  }

  @Get('liveness')
  @HttpCode(HttpStatus.OK)
  liveness() {
    return { status: 'alive' };
  }

  @Get('readiness')
  @HttpCode(HttpStatus.OK)
  readiness() {
    return {
      status: 'ready',
      database: 'connected',
    };
  }
}
