import { Queue, Job } from 'bullmq';

export type QueuePayload = {
  tokens: string[];
};

export class CoinSimilarityEmbeddingsQueue extends Queue<QueuePayload> {}

export class CoinSimilarityEmbeddingsJob extends Job<QueuePayload> {}

export const COIN_SIMILARITY_EMBEDDINGS_QUEUE = 'coin-similarity-embeddings';
