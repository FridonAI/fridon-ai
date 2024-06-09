import { InjectQueue } from '@nestjs/bullmq';
import {
  TRANSACTION_LISTENER_QUEUE,
  TransactionListenerQueue,
  TransactionType,
} from './types';
import { AuxType } from '../events/transaction.event';
import { Injectable, Logger } from '@nestjs/common';

@Injectable()
export class TransactionListenerService {
  private readonly logger = new Logger(TransactionListenerService.name);

  constructor(
    @InjectQueue(TRANSACTION_LISTENER_QUEUE)
    private readonly transactionListenerQueue: TransactionListenerQueue,
  ) {}

  async registerTransactionListener(
    transactionId: string,
    transactionType: TransactionType,
    aux: AuxType,
  ) {
    this.logger.debug(
      `Registering transaction listener for "${transactionType}" transaction[${transactionId}]`,
    );
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
