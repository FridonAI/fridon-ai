import { Injectable } from '@nestjs/common';

@Injectable()
export class LeaderBoardService {
  constructor() {}

  async updateScore(obj: {
    chatId: string;
    walletId: string;
    score: number;
  }): Promise<void> {
    console.log(
      `Updating score for chat ${obj.chatId} and wallet ${obj.walletId} to ${obj.score}`,
    );
  }
}
