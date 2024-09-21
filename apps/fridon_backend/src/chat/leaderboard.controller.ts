import { Controller, Get, UseInterceptors } from '@nestjs/common';

import { ApiOkResponse, ApiTags } from '@nestjs/swagger';
import { LeaderBoardService } from './leaderboard.service';
import { LeaderboardResponseDto } from './leaderboard.dto';
import { CacheInterceptor, CacheTTL } from '@nestjs/cache-manager';

@Controller('leaderboard')
@ApiTags('leaderboard')
export class LeaderboardHttpController {
  constructor(private readonly leaderboardService: LeaderBoardService) {}

  @Get()
  @UseInterceptors(CacheInterceptor)
  @CacheTTL(5) // ToDo: Change to 30 seconds
  @ApiOkResponse({ type: LeaderboardResponseDto })
  async getChats(): Promise<LeaderboardResponseDto> {
    return await this.leaderboardService.getLeaderboard();
  }
}
