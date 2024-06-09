import { InjectQueue } from '@nestjs/bullmq';
import {
  TRANSACTION_LISTENER_QUEUE,
  TransactionListenerQueue,
  TransactionType,
} from './types';
import { AuxType } from '../events/transaction.event';
import { Inject, Injectable, Logger } from '@nestjs/common';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';

@Injectable()
export class TransactionListenerService {
  private readonly logger = new Logger(TransactionListenerService.name);

  constructor(
    @InjectQueue(TRANSACTION_LISTENER_QUEUE)
    private readonly transactionListenerQueue: TransactionListenerQueue,
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
  ) {}

  async registerTransactionListener(
    transactionId: string,
    transactionType: TransactionType,
    aux: AuxType,
  ) {
    this.logger.debug(
      `Registering transaction listener for "${transactionType}" transaction[${transactionId}]`,
    );

    if (transactionType === TransactionType.PAYMENT) {
      await this.registerPluginPurchaseInProgress(aux.walletId, aux.plugin!);
    }

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
  async registerPluginPurchaseInProgress(
    walletAddress: string,
    pluginId: string,
  ) {
    this.logger.debug(
      `Registering plugin purchase in progress for plugin[${pluginId}]`,
    );
    await this.cacheManager.set(
      `plugin_purchase_in_progress_${walletAddress}_${pluginId}`,
      true,
      15 * 1000,
    );
  }

  async getPurchaseInProgressPlugins(walletAddress: string): Promise<string[]> {
    const keys = await this.cacheManager.store.keys();
    const transactions = keys.filter((key) =>
      key.startsWith(`plugin_purchase_in_progress_${walletAddress}`),
    );

    return transactions.map((transaction) => transaction.split('_').pop()!);
  }
}
