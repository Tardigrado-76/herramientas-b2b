import {
  Injectable,
  BadRequestException,
  InternalServerErrorException,
} from '@nestjs/common';
import { SupabaseService } from '../supabase/supabase.service';
import { ClockActionDto } from './dto/clock-action.dto';

export interface TimeEntry {
  id: string;
  user_id: string;
  type: 'IN' | 'OUT' | 'PAUSE_IN' | 'PAUSE_OUT';
  created_at: string;
  recorded_at: string;
  location?: string | null;
  device_info?: string;
  ip_address?: string;
}

export interface OfficeLocation {
  id?: string;
  name: string;
  latitude: number;
  longitude: number;
  radius_meters: number;
}

export function getDistanceFromLatLonInM(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number,
): number {
  const R = 6371e3; // Radius of the earth in meters
  const dLat = deg2rad(lat2 - lat1);
  const dLon = deg2rad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(deg2rad(lat1)) *
      Math.cos(deg2rad(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const d = R * c;
  return d;
}

function deg2rad(deg: number): number {
  return deg * (Math.PI / 180);
}

@Injectable()
export class TimeTrackingService {
  constructor(private readonly supabase: SupabaseService) {}

  private get client() {
    return this.supabase.getClient();
  }

  async getLastEntry(userId: string): Promise<TimeEntry | null> {
    const res = await this.client
      .from('time_entries')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle();

    if (res.error) throw new InternalServerErrorException(res.error.message);
    return (res.data as TimeEntry | null) ?? null;
  }

  private async validateGeofencing(dto: ClockActionDto): Promise<void> {
    if (dto.latitude === undefined || dto.longitude === undefined) {
      return;
    }

    const res = await this.client.from('locations').select('*');

    if (res.error) throw new InternalServerErrorException(res.error.message);

    const locations = (res.data as OfficeLocation[] | null) ?? [];

    if (locations.length > 0) {
      let isWithinPerimeter = false;
      let minDistance = Infinity;
      let closestLocationName = '';

      for (const loc of locations) {
        const dist = getDistanceFromLatLonInM(
          dto.latitude,
          dto.longitude,
          loc.latitude,
          loc.longitude,
        );
        if (dist <= loc.radius_meters) {
          isWithinPerimeter = true;
          break;
        }
        if (dist < minDistance) {
          minDistance = dist;
          closestLocationName = loc.name;
        }
      }

      if (!isWithinPerimeter) {
        throw new BadRequestException(
          `Fichaje bloqueado: Se encuentra fuera del rango permitido de la oficina. ` +
            `La sede más cercana es "${closestLocationName}" a ${Math.round(minDistance)}m. ` +
            `Límite permitido: ${locations[0]?.radius_meters || 500}m.`,
        );
      }
    }
  }

  async clockIn(userId: string, dto: ClockActionDto): Promise<TimeEntry> {
    const lastEntry = await this.getLastEntry(userId);

    if (
      lastEntry &&
      (lastEntry.type === 'IN' ||
        lastEntry.type === 'PAUSE_IN' ||
        lastEntry.type === 'PAUSE_OUT')
    ) {
      throw new BadRequestException('You are already clocked in.');
    }

    await this.validateGeofencing(dto);

    const res = await this.client
      .from('time_entries')
      .insert({
        user_id: userId,
        type: 'IN',
        location:
          dto.latitude && dto.longitude
            ? `POINT(${dto.longitude} ${dto.latitude})`
            : null,
        device_info: dto.device_info,
        ip_address: dto.ip_address,
        recorded_at: dto.recorded_at
          ? new Date(dto.recorded_at).toISOString()
          : new Date().toISOString(),
      })
      .select()
      .single();

    if (res.error) throw new InternalServerErrorException(res.error.message);
    return res.data as TimeEntry;
  }

  async clockOut(userId: string, dto: ClockActionDto): Promise<TimeEntry> {
    const lastEntry = await this.getLastEntry(userId);

    if (!lastEntry || lastEntry.type === 'OUT') {
      throw new BadRequestException('You are not clocked in.');
    }

    await this.validateGeofencing(dto);

    const res = await this.client
      .from('time_entries')
      .insert({
        user_id: userId,
        type: 'OUT',
        location:
          dto.latitude && dto.longitude
            ? `POINT(${dto.longitude} ${dto.latitude})`
            : null,
        device_info: dto.device_info,
        ip_address: dto.ip_address,
        recorded_at: dto.recorded_at
          ? new Date(dto.recorded_at).toISOString()
          : new Date().toISOString(),
      })
      .select()
      .single();

    if (res.error) throw new InternalServerErrorException(res.error.message);
    return res.data as TimeEntry;
  }

  async togglePause(userId: string, dto: ClockActionDto): Promise<TimeEntry> {
    const lastEntry = await this.getLastEntry(userId);

    if (!lastEntry || lastEntry.type === 'OUT') {
      throw new BadRequestException('Cannot pause while not clocked in.');
    }

    await this.validateGeofencing(dto);

    const nextType =
      lastEntry.type === 'IN' || lastEntry.type === 'PAUSE_OUT'
        ? 'PAUSE_IN'
        : 'PAUSE_OUT';

    const res = await this.client
      .from('time_entries')
      .insert({
        user_id: userId,
        type: nextType,
        location:
          dto.latitude && dto.longitude
            ? `POINT(${dto.longitude} ${dto.latitude})`
            : null,
        device_info: dto.device_info,
        ip_address: dto.ip_address,
        recorded_at: dto.recorded_at
          ? new Date(dto.recorded_at).toISOString()
          : new Date().toISOString(),
      })
      .select()
      .single();

    if (res.error) throw new InternalServerErrorException(res.error.message);
    return res.data as TimeEntry;
  }

  async getWeeklySummary(userId: string) {
    const startOfWeek = new Date();
    startOfWeek.setHours(0, 0, 0, 0);
    startOfWeek.setDate(
      startOfWeek.getDate() -
        startOfWeek.getDay() +
        (startOfWeek.getDay() === 0 ? -6 : 1),
    ); // Monday

    const { data, error } = await this.client
      .from('time_entries')
      .select('*')
      .eq('user_id', userId)
      .gte('recorded_at', startOfWeek.toISOString())
      .order('recorded_at', { ascending: true });

    if (error) throw new InternalServerErrorException(error.message);

    let totalSeconds = 0;
    let currentInTime: number | null = null;
    let lastPauseStart: number | null = null;

    const entries = (data as TimeEntry[] | null) ?? [];

    entries.forEach((entry) => {
      const time = new Date(entry.recorded_at).getTime();

      if (entry.type === 'IN') {
        currentInTime = time;
      } else if (entry.type === 'OUT' && currentInTime !== null) {
        totalSeconds += (time - currentInTime) / 1000;
        currentInTime = null;
      } else if (entry.type === 'PAUSE_IN' && currentInTime !== null) {
        totalSeconds += (time - currentInTime) / 1000;
        currentInTime = null;
        lastPauseStart = time;
      } else if (entry.type === 'PAUSE_OUT' && lastPauseStart !== null) {
        currentInTime = time;
        lastPauseStart = null;
      }
    });

    if (currentInTime !== null) {
      totalSeconds += (Date.now() - currentInTime) / 1000;
    }

    return {
      totalSeconds,
      entriesCount: entries.length,
      startOfWeek: startOfWeek.toISOString(),
    };
  }

  async predictClockOut(userId: string) {
    const { data, error } = await this.client
      .from('time_entries')
      .select('recorded_at')
      .eq('user_id', userId)
      .eq('type', 'OUT')
      .order('recorded_at', { ascending: false })
      .limit(10);

    const entries = (data as Array<{ recorded_at: string }> | null) ?? [];

    if (error || entries.length === 0) {
      const today = new Date();
      today.setHours(18, 0, 0, 0);
      return { predictedTime: today.toISOString() };
    }

    let totalMinutes = 0;
    entries.forEach((entry) => {
      const d = new Date(entry.recorded_at);
      totalMinutes += d.getHours() * 60 + d.getMinutes();
    });

    const avgMinutes = totalMinutes / entries.length;
    const predicted = new Date();
    predicted.setHours(
      Math.floor(avgMinutes / 60),
      Math.floor(avgMinutes % 60),
      0,
      0,
    );

    return { predictedTime: predicted.toISOString() };
  }

  async getMonthlySummary(userId: string) {
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

    const { data, error } = await this.client
      .from('time_entries')
      .select('*')
      .eq('user_id', userId)
      .gte('recorded_at', startOfMonth.toISOString())
      .order('recorded_at', { ascending: true });

    if (error) throw new InternalServerErrorException(error.message);

    const dailyMap = new Map<string, number>();
    let currentInTime: number | null = null;
    let lastPauseStart: number | null = null;

    const entries = (data as TimeEntry[] | null) ?? [];

    entries.forEach((entry) => {
      const dateStr = entry.recorded_at.split('T')[0]; // YYYY-MM-DD
      const time = new Date(entry.recorded_at).getTime();

      if (!dailyMap.has(dateStr)) dailyMap.set(dateStr, 0);

      if (entry.type === 'IN') {
        currentInTime = time;
      } else if (entry.type === 'OUT' && currentInTime !== null) {
        const duration = (time - currentInTime) / 1000;
        dailyMap.set(dateStr, dailyMap.get(dateStr)! + duration);
        currentInTime = null;
      } else if (entry.type === 'PAUSE_IN' && currentInTime !== null) {
        const duration = (time - currentInTime) / 1000;
        dailyMap.set(dateStr, dailyMap.get(dateStr)! + duration);
        currentInTime = null;
        lastPauseStart = time;
      } else if (entry.type === 'PAUSE_OUT' && lastPauseStart !== null) {
        currentInTime = time;
        lastPauseStart = null;
      }
    });

    if (currentInTime !== null) {
      const todayStr = now.toISOString().split('T')[0];
      if (!dailyMap.has(todayStr)) dailyMap.set(todayStr, 0);
      dailyMap.set(
        todayStr,
        dailyMap.get(todayStr)! + (Date.now() - currentInTime) / 1000,
      );
    }

    const dailyData = Array.from(dailyMap.entries()).map(([date, seconds]) => ({
      date,
      hours: parseFloat((seconds / 3600).toFixed(2)),
    }));

    return {
      month: now.toLocaleString('default', { month: 'long' }),
      year: now.getFullYear(),
      dailyData,
    };
  }
}
