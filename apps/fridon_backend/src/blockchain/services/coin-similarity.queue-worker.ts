import { OnWorkerEvent, Processor, WorkerHost } from '@nestjs/bullmq';
import {
  COIN_SIMILARITY_EMBEDDINGS_QUEUE,
  CoinSimilarityEmbeddingsJob,
} from './types';
import { Inject, Logger } from '@nestjs/common';
import { CoinSimilarityService } from './coin-similarity';

@Processor(COIN_SIMILARITY_EMBEDDINGS_QUEUE)
export class CoinSimilarityEmbeddingsWorker extends WorkerHost {
  private readonly logger = new Logger();
  @Inject() private readonly coinSimilarityService: CoinSimilarityService;

  async process(job: CoinSimilarityEmbeddingsJob): Promise<any> {
    const tokenList = job.data.tokens.map((t) => t);
    this.logger.debug(
      `Processing Tokens: [${tokenList}]`,
      `Embeddings[${job.id}]`,
    );
    await this.coinSimilarityService.updateEmbeddingsBatch(job.data.tokens);

    this.logger.debug(`Processed`, `Embeddings[${job.id}]`);
  }

  @OnWorkerEvent('failed')
  onError(obj: { id: number; failedReason: string }) {
    if (!obj) {
      this.logger.error(`Failed: unknown reason`);
      return;
    }
    this.logger.error(`Failed: ${obj.failedReason}`, `Embeddings[${obj.id}]`);
  }
}
