import {
  Controller,
  Post,
  Body,
  UseGuards,
  Request,
  Get,
  InternalServerErrorException,
} from '@nestjs/common';
import { TimeTrackingService } from './time-tracking.service';
import { SupabaseAuthGuard } from '../auth/supabase-auth.guard';
import { ClockActionDto } from './dto/clock-action.dto';

export interface AuthenticatedRequest {
  user: {
    sub: string;
    email?: string;
  };
}

@Controller('time-entries')
@UseGuards(SupabaseAuthGuard)
export class TimeTrackingController {
  constructor(private readonly timeTrackingService: TimeTrackingService) {}

  @Get('current')
  async getCurrentStatus(@Request() req: AuthenticatedRequest) {
    try {
      console.log(
        'GET /time-entries/current called for user:',
        req.user?.email,
      );
      return await this.timeTrackingService.getLastEntry(req.user.sub);
    } catch (error: unknown) {
      const err = error instanceof Error ? error : new Error(String(error));
      console.error('❌ Error in getCurrentStatus:', err.message, err.stack);
      throw new InternalServerErrorException(err.message);
    }
  }

  @Post('in')
  async clockIn(
    @Request() req: AuthenticatedRequest,
    @Body() dto: ClockActionDto,
  ) {
    return this.timeTrackingService.clockIn(req.user.sub, dto);
  }

  @Post('out')
  async clockOut(
    @Request() req: AuthenticatedRequest,
    @Body() dto: ClockActionDto,
  ) {
    return this.timeTrackingService.clockOut(req.user.sub, dto);
  }

  @Post('pause')
  async togglePause(
    @Request() req: AuthenticatedRequest,
    @Body() dto: ClockActionDto,
  ) {
    return this.timeTrackingService.togglePause(req.user.sub, dto);
  }

  @Get('weekly-summary')
  async getWeeklySummary(@Request() req: AuthenticatedRequest) {
    return this.timeTrackingService.getWeeklySummary(req.user.sub);
  }

  @Get('monthly-summary')
  async getMonthlySummary(@Request() req: AuthenticatedRequest) {
    return this.timeTrackingService.getMonthlySummary(req.user.sub);
  }

  @Get('predict-out')
  async predictClockOut(@Request() req: AuthenticatedRequest) {
    return this.timeTrackingService.predictClockOut(req.user.sub);
  }
}
