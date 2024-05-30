import { InjectQueue } from '@nestjs/bullmq';
import { TRANSACTION_LISTENER_QUEUE, TransactionListenerQueue } from './types';
import { AuxType } from '../events/transaction.event';
import { Injectable } from '@nestjs/common';

@Injectable()
export class TransactionListenerService {
  constructor(
    @InjectQueue(TRANSACTION_LISTENER_QUEUE)
    private readonly transactionListenerQueue: TransactionListenerQueue,
  ) {}

  async registerTransactionListener(
    transactionId: string,
    transactionType: string,
    aux: AuxType,
  ) {
    await this.transactionListenerQueue.add(
      transactionId,
      {
        transactionId: transactionId,
        transactionType: transactionType,
        count: 0,
        aux: aux,
      },
      { delay: 3000 },
    );
  }
}
