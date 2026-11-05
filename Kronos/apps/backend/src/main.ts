import { NestFactory } from '@nestjs/core';
import { ValidationPipe, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Request, Response, NextFunction } from 'express';
import helmet from 'helmet';
import { AppModule } from './app.module';

async function bootstrap() {
  const logger = new Logger('Bootstrap');
  const app = await NestFactory.create(AppModule);
  const configService = app.get(ConfigService);

  // 1. Production HTTP Security Headers (Helmet)
  app.use(
    helmet({
      contentSecurityPolicy:
        process.env.NODE_ENV === 'production' ? undefined : false,
      crossOriginEmbedderPolicy: false,
    }),
  );

  // 2. Strict CORS Configuration
  const rawOrigins = configService.get<string>(
    'ALLOWED_ORIGINS',
    'http://localhost:3000,https://api.tavilga.es,https://tavilga.es',
  );
  const allowedOrigins = rawOrigins.split(',').map((origin) => origin.trim());

  app.enableCors({
    origin: (
      origin: string | undefined,
      callback: (err: Error | null, allow?: boolean) => void,
    ) => {
      // Allow requests with no origin (mobile apps, server-to-server, curl)
      if (
        !origin ||
        allowedOrigins.includes(origin) ||
        allowedOrigins.includes('*')
      ) {
        callback(null, true);
      } else {
        logger.warn(`Blocked by CORS: ${origin}`);
        callback(new Error(`Origin ${origin} not allowed by CORS policy`));
      }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: [
      'Content-Type',
      'Authorization',
      'X-Requested-With',
      'Accept',
    ],
  });

  // 3. Global Validation & Sanitization Pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  // 4. Request Logging Middleware
  app.use((req: Request, res: Response, next: NextFunction) => {
    const start = Date.now();
    res.on('finish', () => {
      const duration = Date.now() - start;
      logger.log(
        `[${req.method}] ${req.originalUrl || req.url} - ${res.statusCode} (${duration}ms)`,
      );
    });
    next();
  });

  // 5. Graceful Shutdown Hooks
  app.enableShutdownHooks();

  const port = configService.get<number>('PORT', 3001);
  await app.listen(port, '0.0.0.0');
  logger.log(
    `🚀 Kronos Backend running in ${process.env.NODE_ENV || 'development'} mode on port ${port}`,
  );
}

void bootstrap();
