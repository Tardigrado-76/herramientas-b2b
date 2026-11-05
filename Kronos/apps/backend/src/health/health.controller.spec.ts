import { Test, TestingModule } from '@nestjs/testing';
import { ConfigService } from '@nestjs/config';
import { HealthController } from './health.controller';

describe('HealthController', () => {
  let controller: HealthController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [HealthController],
      providers: [
        {
          provide: ConfigService,
          useValue: {
            get: jest
              .fn()
              .mockImplementation(
                (_key: string, defaultValue: string) => defaultValue,
              ),
          },
        },
      ],
    }).compile();

    controller = module.get<HealthController>(HealthController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });

  it('should return health status ok', () => {
    const health = controller.check();
    expect(health.status).toBe('ok');
    expect(health).toHaveProperty('timestamp');
    expect(health).toHaveProperty('uptime');
  });

  it('should return liveness alive', () => {
    expect(controller.liveness()).toEqual({ status: 'alive' });
  });

  it('should return readiness ready', () => {
    expect(controller.readiness()).toEqual({
      status: 'ready',
      database: 'connected',
    });
  });
});
