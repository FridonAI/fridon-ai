import { Injectable } from '@nestjs/common';
import { PrismaService } from 'nestjs-prisma';
import { LeaderboardResponseDto } from './leaderboard.dto';

@Injectable()
export class LeaderBoardService {
  constructor(private readonly prisma: PrismaService) {}

  async updateScore(obj: {
    chatId?: string;
    walletId: string;
    score?: number;
    transactionsMade?: number;
    plugins?: string[];
    myPluginsUsed?: number;
  }): Promise<void> {
    if (obj.chatId) {
      await this.prisma.walletScoreHistory.create({
        data: {
          score: obj.score ?? 0,
          walletId: obj.walletId,
          chatId: obj.chatId,
        },
      });
    }

    await this.prisma.leaderboard.upsert({
      where: { walletId: obj.walletId },
      update: {
        score: { increment: obj.score ?? 0 },
        pluginsUsed: { increment: obj.plugins?.length ?? 0 },
        transactionsMade: { increment: obj.transactionsMade ?? 0 },
        myPluginsUsed: { increment: obj.myPluginsUsed ?? 0 },
      },
      create: {
        walletId: obj.walletId,
        score: obj.score ?? 0,
        pluginsUsed: obj.plugins?.length ?? 0,
        myPluginsUsed: obj.myPluginsUsed ?? 0,
        transactionsMade: obj.transactionsMade ?? 0,
      },
    });
  }

  async getLeaderboard(): Promise<LeaderboardResponseDto> {
    const leaderboard = await this.prisma.leaderboard.findMany({
      orderBy: { score: 'desc' },
    });

    return new LeaderboardResponseDto({
      leaderboard: leaderboard.map((row, index) => ({
        rank: index + 1,
        walletId: row.walletId,
        score: row.score,
        pluginsUsed: row.pluginsUsed,
        myPluginsUsed: row.myPluginsUsed,
        transactionsMade: row.transactionsMade,
      })),
    });
  }

  async getWalletPosition(walletId: string): Promise<number> {
    const leaderboard = await this.prisma.leaderboard.findMany({
      orderBy: { score: 'desc' },
      select: { walletId: true },
    });

    const position = leaderboard.findIndex((row) => row.walletId === walletId);

    return position === -1 ? 0 : position + 1;
  }
}
