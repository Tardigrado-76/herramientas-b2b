import { Test, TestingModule } from '@nestjs/testing';
import { BadRequestException } from '@nestjs/common';
import {
  TimeTrackingService,
  getDistanceFromLatLonInM,
  TimeEntry,
} from './time-tracking.service';
import { SupabaseService } from '../supabase/supabase.service';

describe('TimeTrackingService', () => {
  let service: TimeTrackingService;
  let lastEntryMock: TimeEntry | null = null;
  let insertedRecords: Array<Record<string, unknown>> = [];
  let locationsMock = [
    {
      id: 'loc-1',
      name: 'Sede Central Madrid Sol',
      latitude: 40.4168,
      longitude: -3.7038,
      radius_meters: 500,
    },
  ];

  const mockSupabaseClient = {
    from: jest.fn((table: string) => {
      if (table === 'locations') {
        return {
          select: jest
            .fn()
            .mockResolvedValue({ data: locationsMock, error: null }),
        };
      }
      if (table === 'time_entries') {
        return {
          select: jest.fn(() => ({
            eq: jest.fn(() => ({
              order: jest.fn(() => ({
                limit: jest.fn(() => ({
                  maybeSingle: jest
                    .fn()
                    .mockResolvedValue({ data: lastEntryMock, error: null }),
                })),
              })),
              gte: jest.fn(() => ({
                order: jest.fn().mockResolvedValue({
                  data: insertedRecords,
                  error: null,
                }),
              })),
            })),
          })),
          insert: jest.fn((payload: Record<string, unknown>) => ({
            select: jest.fn(() => ({
              single: jest.fn().mockImplementation(() => {
                const created: TimeEntry = {
                  id: `entry-${insertedRecords.length + 1}`,
                  user_id: String(payload.user_id),
                  type: payload.type as TimeEntry['type'],
                  created_at: new Date().toISOString(),
                  recorded_at: String(payload.recorded_at),
                };
                insertedRecords.push(
                  created as unknown as Record<string, unknown>,
                );
                lastEntryMock = created;
                return Promise.resolve({ data: created, error: null });
              }),
            })),
          })),
        };
      }
      return {};
    }),
  };

  beforeEach(async () => {
    lastEntryMock = null;
    insertedRecords = [];
    locationsMock = [
      {
        id: 'loc-1',
        name: 'Sede Central Madrid Sol',
        latitude: 40.4168,
        longitude: -3.7038,
        radius_meters: 500,
      },
    ];

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        TimeTrackingService,
        {
          provide: SupabaseService,
          useValue: {
            getClient: () => mockSupabaseClient,
          },
        },
      ],
    }).compile();

    service = module.get<TimeTrackingService>(TimeTrackingService);
  });

  describe('Haversine Geofencing (500m radius)', () => {
    it('calculates Haversine distance accurately within 500m', () => {
      const dist = getDistanceFromLatLonInM(40.4168, -3.7038, 40.417, -3.704);
      expect(dist).toBeGreaterThan(0);
      expect(dist).toBeLessThan(500);
    });

    it('approves clock-in when coordinates are within 500m (lat: 40.4170, lng: -3.7040)', async () => {
      const entry = await service.clockIn('user-1', {
        latitude: 40.417,
        longitude: -3.704,
        device_info: 'Jest Test Runner',
      });
      expect(entry.type).toBe('IN');
      expect(entry.user_id).toBe('user-1');
    });

    it('rejects clock-in with BadRequestException when coordinates are outside 500m (lat: 40.4500, lng: -3.6900)', async () => {
      await expect(
        service.clockIn('user-1', {
          latitude: 40.45,
          longitude: -3.69,
        }),
      ).rejects.toThrow(BadRequestException);
    });
  });

  describe('Clock State Machine (IN -> PAUSE_IN -> PAUSE_OUT -> OUT)', () => {
    it('executes complete valid state transition IN -> PAUSE_IN -> PAUSE_OUT -> OUT', async () => {
      // 1. Clock IN
      const s1 = await service.clockIn('user-1', {});
      expect(s1.type).toBe('IN');

      // 2. Toggle Pause -> PAUSE_IN
      const s2 = await service.togglePause('user-1', {});
      expect(s2.type).toBe('PAUSE_IN');

      // 3. Toggle Pause -> PAUSE_OUT
      const s3 = await service.togglePause('user-1', {});
      expect(s3.type).toBe('PAUSE_OUT');

      // 4. Clock OUT -> OUT
      const s4 = await service.clockOut('user-1', {});
      expect(s4.type).toBe('OUT');
    });

    it('throws BadRequestException on duplicate IN when already clocked in', async () => {
      await service.clockIn('user-1', {});
      await expect(service.clockIn('user-1', {})).rejects.toThrow(
        new BadRequestException('You are already clocked in.'),
      );
    });

    it('throws BadRequestException when attempting OUT or PAUSE while clocked OUT', async () => {
      await expect(service.clockOut('user-1', {})).rejects.toThrow(
        new BadRequestException('You are not clocked in.'),
      );
      await expect(service.togglePause('user-1', {})).rejects.toThrow(
        new BadRequestException('Cannot pause while not clocked in.'),
      );
    });
  });
});
