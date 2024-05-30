import { Logger } from '@nestjs/common';
import { EventsHandler } from '@nestjs/cqrs';
import {
  TransactionConfirmedEvent,
  TransactionFailedEvent,
  TransactionSkippedEvent,
} from 'src/blockchain/events/transaction.event';
import { TransactionType } from 'src/blockchain/transaction-listener/types';

@EventsHandler(TransactionConfirmedEvent)
export class TransactionConfirmedHandler {
  private readonly logger = new Logger(TransactionConfirmedHandler.name);

  async handle(event: TransactionConfirmedEvent) {
    if (event.transactionType !== TransactionType.PAYMENT) return;

    this.logger.debug(`Processing PaymentTransaction[${event.transactionId}]`);
    // ToDo: Process payment transaction
  }
}

@EventsHandler(TransactionSkippedEvent)
export class TransactionSkippedHandler {
  private readonly logger = new Logger(TransactionSkippedHandler.name);

  async handle(event: TransactionSkippedEvent) {
    if (event.transactionType !== TransactionType.PAYMENT) return;

    this.logger.debug(`Skipping PaymentTransaction[${event.transactionId}]`);
  }
}

@EventsHandler(TransactionFailedEvent)
export class TransactionFailedHandler {
  private readonly logger = new Logger(TransactionFailedHandler.name);

  async handle(event: TransactionFailedEvent) {
    if (event.transactionType !== TransactionType.PAYMENT) return;

    this.logger.debug(`Failed PaymentTransaction[${event.transactionId}]`);
  }
}
