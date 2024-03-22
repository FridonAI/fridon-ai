import { InjectQueue, Processor, WorkerHost } from '@nestjs/bullmq';
import {
  TRANSACTION_LISTENER_QUEUE,
  TransactionListenerJob,
  TransactionListenerQueue,
} from './types';
import { Connection } from '@solana/web3.js';
import { Logger } from '@nestjs/common';

@Processor(TRANSACTION_LISTENER_QUEUE)
export class TransactionListenerProcessor extends WorkerHost {
  private readonly logger = new Logger(TransactionListenerProcessor.name);

  constructor(
    private readonly connection: Connection,
    @InjectQueue(TRANSACTION_LISTENER_QUEUE)
    private readonly transactionListenerQueue: TransactionListenerQueue,
  ) {
    super();
  }

  async process(job: TransactionListenerJob): Promise<any> {
    const txId = job.data.transactionId;
    const tx = await this.connection.getTransaction(txId, {
      commitment: 'confirmed',
      maxSupportedTransactionVersion: 0,
    });

    if (tx && tx.meta?.err) {
      this.logger.debug(
        `Transaction[${txId}] has failed with error: ${tx.meta.err}`,
      );
      return;
    }

    if (tx && tx.transaction) {
      this.logger.debug(`Transaction[${txId}] has succeeded`);
      return;
    }

    if (job.data.count >= 10) {
      this.logger.debug(
        `Transaction[${txId}] has been skipped after 10 retries`,
      );
      return;
    }

    this.logger.debug(
      `Transaction[${txId}] has not been confirmed yet. Retrying... count=${job.data.count + 1}`,
    );
    job.data.count++;
    await this.transactionListenerQueue.add('', job.data, {
      delay: 1000,
    });
  }
}
