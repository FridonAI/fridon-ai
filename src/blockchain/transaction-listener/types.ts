import { Queue, Worker, Job } from 'bullmq';

export type QueuePayload = {
  transactionId: string;
  aux?: object;
};

export class TransactionListenerQueue extends Queue<QueuePayload> {}

export class TransactionListenerWorker extends Worker<QueuePayload> {}

export class TransactionListenerJob extends Job<QueuePayload> {}

export const TRANSACTION_LISTENER_QUEUE = 'transaction-listener';
