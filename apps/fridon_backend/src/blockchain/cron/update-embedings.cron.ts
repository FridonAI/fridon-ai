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
    const envName = 'ENABLE_UPDATE_EMBEDDINGS_CRON';
    if (process.env['ENABLE_UPDATE_EMBEDDINGS_CRON'] !== '1') {
      this.l.debug(
        `Update Embeddings Cron Job is disabled (Set ${envName}=1 to enable)`,
      );
      return;
    }

    this.l.debug(
      `Called Update Embeddings Cron Job (remove ${envName} to disable)`,
    );
    await this.updateEmbeddings();
  }

  async updateEmbeddings() {
    const tokens = this.coinSimilarityService.getTokens();

    const chunks = _.chunk(tokens, 16);

    type T = Parameters<CoinSimilarityEmbeddingsQueue['addBulk']>[0][number];
    const queueBatchData = chunks.map((chunk, i): T => {
      return {
        name: `update-embeddings-${i}`,
        data: { tokens: chunk },
        opts: {
          attempts: 3,
          backoff: {
            type: 'exponential',
            delay: 5000,
          },
        },
      };
    });

    await this.transactionListenerQueue.addBulk(queueBatchData);
  }

  onApplicationBootstrap() {
    const envName = 'UPDATE_EMBEDDINGS_ON_BOOTSTRAP';
    if (process.env[envName] !== '1') {
      this.l.debug(
        `Application Bootstrap: Skipping Update Embeddings (Set ${envName}=1 to enable)`,
      );
      return;
    }
    this.l.debug('Application Bootstrap: Updating Embeddings');
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    this.updateEmbeddings().then(() => {
      this.l.debug('Application Bootstrap: Embeddings Updated');
    });
  }
}
