import { Queue, Job } from 'bullmq';
import { TokenAddress } from './coin-similarity';

export type QueuePayload = {
  tokenAddresses: TokenAddress[];
};

export class CoinSimilarityEmbeddingsQueue extends Queue<QueuePayload> {}

export class CoinSimilarityEmbeddingsJob extends Job<QueuePayload> {}

export const COIN_SIMILARITY_EMBEDDINGS_QUEUE = 'coin-similarity-embeddings';
