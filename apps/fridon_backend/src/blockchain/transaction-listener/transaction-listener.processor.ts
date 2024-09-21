import { InjectQueue, Processor, WorkerHost } from '@nestjs/bullmq';
import {
  TRANSACTION_LISTENER_QUEUE,
  TransactionListenerJob,
  TransactionListenerQueue,
} from './types';
import { Connection } from '@solana/web3.js';
import { Logger } from '@nestjs/common';
import { EventBus } from '@nestjs/cqrs';
import {
  TransactionConfirmedEvent,
  TransactionFailedEvent,
  TransactionSkippedEvent,
} from '../events/transaction.event';

@Processor(TRANSACTION_LISTENER_QUEUE)
export class TransactionListenerProcessor extends WorkerHost {
  private readonly logger = new Logger(TransactionListenerProcessor.name);

  constructor(
    private readonly connection: Connection,
    @InjectQueue(TRANSACTION_LISTENER_QUEUE)
    private readonly transactionListenerQueue: TransactionListenerQueue,
    private readonly eventBus: EventBus,
  ) {
    super();
  }

  async process(job: TransactionListenerJob): Promise<any> {
    const txId = job.data.transactionId;
    const txType = job.data.transactionType;

    const tx = await this.connection.getTransaction(txId, {
      commitment: 'confirmed',
      maxSupportedTransactionVersion: 0,
    });

    // 1. Failed Transaction
    if (tx && tx.meta?.err) {
      this.logger.debug(
        `Transaction[${txId}] has failed with error: ${tx.meta.err}`,
      );
      return this.eventBus.publish(
        new TransactionFailedEvent({
          transactionId: txId,
          transactionType: job.data.transactionType,
          aux: job.data.aux,
        }),
      );
    }

    // 2. Confirmed Transaction
    if (tx && tx.transaction) {
      this.logger.debug(`Transaction[${txType}|${txId}] has succeeded`);
      return this.eventBus.publish(
        new TransactionConfirmedEvent({
          transactionId: txId,
          transactionType: job.data.transactionType,
          aux: job.data.aux,
        }),
      );
    }

    // 3. Transaction Skipped
    const retryMaxCount = 10;
    if (job.data.count >= retryMaxCount) {
      this.logger.debug(
        `Transaction[${txId}] has been skipped after ${retryMaxCount} retries`,
      );
      return this.eventBus.publish(
        new TransactionSkippedEvent({
          transactionId: txId,
          transactionType: job.data.transactionType,
          aux: job.data.aux,
        }),
      );
    }

    // 4. Retry
    this.logger.debug(
      `Transaction[${txId}] has not been confirmed yet. Retrying... count=${job.data.count + 1}`,
    );
    job.data.count++;
    await this.transactionListenerQueue.add(txId, job.data, {
      delay: 3000,
    });
  }
}
