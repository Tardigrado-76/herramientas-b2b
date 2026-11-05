import { Test, TestingModule } from '@nestjs/testing';
import { TimeTrackingController } from './time-tracking.controller';
import { TimeTrackingService } from './time-tracking.service';

describe('TimeTrackingController', () => {
  let controller: TimeTrackingController;
  let mockService: Record<string, jest.Mock>;

  beforeEach(async () => {
    mockService = {
      getLastEntry: jest.fn().mockResolvedValue({ id: '1', type: 'IN' }),
      clockIn: jest.fn().mockResolvedValue({ id: '2', type: 'IN' }),
      clockOut: jest.fn().mockResolvedValue({ id: '3', type: 'OUT' }),
      togglePause: jest.fn().mockResolvedValue({ id: '4', type: 'PAUSE_IN' }),
      getWeeklySummary: jest
        .fn()
        .mockResolvedValue({ totalSeconds: 3600, entriesCount: 2 }),
      getMonthlySummary: jest
        .fn()
        .mockResolvedValue({ month: 'October', year: 2026, dailyData: [] }),
      predictClockOut: jest
        .fn()
        .mockResolvedValue({ predictedTime: '2026-10-29T18:00:00.000Z' }),
    };

    const module: TestingModule = await Test.createTestingModule({
      controllers: [TimeTrackingController],
      providers: [
        {
          provide: TimeTrackingService,
          useValue: mockService,
        },
      ],
    }).compile();

    controller = module.get<TimeTrackingController>(TimeTrackingController);
  });

  const mockReq = {
    user: {
      sub: 'user-123',
      email: 'test@tavilga.es',
    },
  };

  it('delegates clockIn, togglePause, clockOut and summaries to TimeTrackingService', async () => {
    const inRes = await controller.clockIn(mockReq, {
      latitude: 40.4168,
      longitude: -3.7038,
    });
    expect(inRes.type).toBe('IN');
    expect(mockService.clockIn).toHaveBeenCalledWith('user-123', {
      latitude: 40.4168,
      longitude: -3.7038,
    });

    const pauseRes = await controller.togglePause(mockReq, {});
    expect(pauseRes.type).toBe('PAUSE_IN');

    const outRes = await controller.clockOut(mockReq, {});
    expect(outRes.type).toBe('OUT');

    const weekly = await controller.getWeeklySummary(mockReq);
    expect(weekly.totalSeconds).toBe(3600);
  });
});
