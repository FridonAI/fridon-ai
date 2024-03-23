import { InjectQueue } from '@nestjs/bullmq';
import { TransactionListenerQueue } from './types';
import { AuxType } from '../events/transaction.event';
import { Injectable } from '@nestjs/common';

@Injectable()
export class TransactionListenerService {
  constructor(
    @InjectQueue('transaction-listener')
    private readonly transactionListenerQueue: TransactionListenerQueue,
  ) {}

  async registerTransactionListener(transactionId: string, aux: AuxType) {
    await this.transactionListenerQueue.add(
      transactionId,
      { transactionId: transactionId, count: 0, aux: aux },
      { delay: 3000 },
    );
  }
}
