import { Queue, Job } from 'bullmq';
import { AuxType } from '../events/transaction.event';

export type QueuePayload = {
  transactionId: string;
  transactionType: string;
  count: number;
  aux: AuxType;
};

export class TransactionListenerQueue extends Queue<QueuePayload> {}

export class TransactionListenerJob extends Job<QueuePayload> {}

export const TRANSACTION_LISTENER_QUEUE = 'transaction-listener';

export enum TransactionType {
  CHAT = 'chatTransaction',
}
