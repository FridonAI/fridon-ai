import { BaseDto } from '@lib/common';
import { ApiProperty } from '@nestjs/swagger';

// Get Leaderboard
export class LeaderboardRowResponseDto extends BaseDto<LeaderboardRowResponseDto> {
  @ApiProperty({ example: 1 })
  rank: number;

  @ApiProperty({ example: '6Uj4wUCtHKieQ7upZivYnQZnzGdfg3xEbSV5YJmsiV3e' })
  walletId: string;

  @ApiProperty({ example: 100 })
  score: number;

  @ApiProperty({ example: 142 })
  pluginsUsed: number;

  @ApiProperty({ example: 23 })
  myPluginsUsed: number;

  @ApiProperty({ example: 4 })
  transactionsMade: number;
}

export class LeaderboardResponseDto extends BaseDto<LeaderboardResponseDto> {
  @ApiProperty({ isArray: true, type: LeaderboardRowResponseDto })
  leaderboard: LeaderboardRowResponseDto[];
}
