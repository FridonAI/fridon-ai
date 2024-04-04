import { Injectable, Logger, OnApplicationBootstrap } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { CoinSimilarityService } from '../services/coin-similarity';
import _ from 'lodash';
import { InjectQueue } from '@nestjs/bullmq';
import {
  COIN_SIMILARITY_EMBEDDINGS_QUEUE,
  CoinSimilarityEmbeddingsQueue,
} from '../services/types';

@Injectable()
export class UpdateEmbeddings implements OnApplicationBootstrap {
  private readonly l = new Logger(UpdateEmbeddings.name);

  constructor(
    private readonly coinSimilarityService: CoinSimilarityService,
    @InjectQueue(COIN_SIMILARITY_EMBEDDINGS_QUEUE)
    private readonly transactionListenerQueue: CoinSimilarityEmbeddingsQueue,
  ) {}

  @Cron(CronExpression.EVERY_HOUR)
  async execute() {
    this.l.debug('Called Update Embeddings Cron Job');
    await this.updateEmbeddings();
  }

  async updateEmbeddings() {
    const tokenAddresses = this.coinSimilarityService.getTokenAddresses();

    const chunks = _.chunk(tokenAddresses, 16);

    type T = Parameters<CoinSimilarityEmbeddingsQueue['addBulk']>[0][number];
    const queueBatchData = chunks.map((chunk, i): T => {
      return {
        name: `update-embeddings-${i}`,
        data: { tokenAddresses: chunk },
      };
    });

    await this.transactionListenerQueue.addBulk(queueBatchData);
  }

  onApplicationBootstrap() {
    this.l.debug('Application Bootstrap: Updating Embeddings');
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    this.updateEmbeddings().then(() => {
      this.l.debug('Application Bootstrap: Embeddings Updated');
    });
  }
}
