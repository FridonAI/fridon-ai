import { Injectable, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { CoinSimilarityService } from '../services/coin-similarity';

@Injectable()
export class UpdateEmbeddings {
  private readonly l = new Logger(UpdateEmbeddings.name);

  constructor(private readonly coinSimilarityService: CoinSimilarityService) {}

  @Cron(CronExpression.EVERY_HOUR)
  async execute() {
    this.l.debug('Called Update Embeddings Cron Job');
    await this.coinSimilarityService.updateAllEmbeddings();
  }
}
