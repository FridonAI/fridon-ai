import { Logger } from '@nestjs/common';
import { EventsHandler } from '@nestjs/cqrs';
import { isNil } from 'lodash';
import {
  TransactionConfirmedEvent,
  TransactionFailedEvent,
  TransactionSkippedEvent,
} from 'src/blockchain/events/transaction.event';
import { TransactionType } from 'src/blockchain/transaction-listener/types';
import { PluginsService } from 'src/plugins/plugins.service';
import { UserService } from '../user.service';

@EventsHandler(TransactionConfirmedEvent)
export class TransactionConfirmedHandler {
  constructor(
    private readonly pluginsService: PluginsService,
    private readonly userService: UserService,
  ) {}

  private readonly logger = new Logger(TransactionConfirmedHandler.name);

  async handle(event: TransactionConfirmedEvent) {
    if (event.transactionType !== TransactionType.PAYMENT) return;

    this.logger.debug(`Processing PaymentTransaction[${event.transactionId}]`);

    if (isNil(event.aux.plugin)) {
      this.logger.debug(
        `Plugin not found for PaymentTransaction[${event.transactionId}]`,
      );
      return;
    }

    this.logger.debug(
      `Plugin[${event.aux.plugin}] found for PaymentTransaction[${event.transactionId}]`,
    );

    const plugin = this.pluginsService.get(event.aux.plugin);
    if (!plugin) {
      this.logger.debug(`Plugin[${event.aux.plugin}] not found`);
      return;
    }

    // date is now plus 3 month
    const expirationDate = new Date();
    expirationDate.setMonth(expirationDate.getMonth() + 3);

    this.logger.debug(`Plugin[${plugin.name}] found`);
    await this.userService.assignPlugin({
      walletId: event.aux.walletId,
      pluginId: plugin,
      // ToDo: Calculate expiration date, default now plus 3 month
      expiresAt: expirationDate,
    });
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
