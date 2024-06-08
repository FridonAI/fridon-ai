import { Controller, Get } from '@nestjs/common';

import { ApiOkResponse, ApiTags } from '@nestjs/swagger';
import { LeaderBoardService } from './leaderboard.service';
import { LeaderboardResponseDto } from './leaderboard.dto';

@Controller('leaderboard')
@ApiTags('leaderboard')
export class LeaderboardHttpController {
  constructor(private readonly leaderboardService: LeaderBoardService) {}

  @Get()
  @ApiOkResponse({ type: LeaderboardResponseDto })
  async getChats(): Promise<LeaderboardResponseDto> {
    return await this.leaderboardService.getLeaderboard();
  }
}
