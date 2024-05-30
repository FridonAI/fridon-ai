import { Injectable } from '@nestjs/common';
import { PrismaService } from 'nestjs-prisma';

@Injectable()
export class LeaderBoardService {
  constructor(private readonly prisma: PrismaService) {}

  async updateScore(obj: {
    chatId: string;
    walletId: string;
    score: number;
  }): Promise<void> {
    await this.prisma.walletScoreHistory.create({
      data: {
        score: obj.score,
        walletId: obj.walletId,
      },
    });
    await this.prisma.leaderboard.upsert({
      where: { walletId: obj.walletId },
      update: {
        score: { increment: obj.score },
      },
      create: {
        walletId: obj.walletId,
        score: obj.score,
      },
    });
  }
}
