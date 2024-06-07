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
import { Connection, ParsedInstruction } from '@solana/web3.js';

@EventsHandler(TransactionConfirmedEvent)
export class TransactionConfirmedHandler {
  constructor(
    private readonly pluginsService: PluginsService,
    private readonly userService: UserService,
    private readonly connection: Connection,
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

    // Transaction Validation
    // todo: replace this with actual values.
    const destinationAddress = '9WP1Wk2wbbDYuuHz7fJmauMhEuPhLSQ1mk8ioY1s4TNj';
    const requiredAmount = 1000;

    const flag = await this.validateTransaction(
      event.transactionId,
      event.aux.walletId,
      requiredAmount,
      destinationAddress,
    );

    if (!flag) {
      this.logger.debug(
        `Transaction[${event.transactionId}] validation failed for plugin[${plugin.name}]`,
      );
      return;
    }

    // date is now plus 3 month
    const expirationDate = new Date();
    expirationDate.setMonth(expirationDate.getMonth() + 3);

    this.logger.debug(`Plugin[${plugin.name}] found`);
    await this.userService.assignPlugin({
      walletId: event.aux.walletId,
      pluginId: plugin.name,
      // ToDo: Calculate expiration date, default now plus 3 month
      expiresAt: expirationDate,
    });
  }

  private async validateTransaction(
    txId: string,
    walletId: string,
    requiredAmount: number,
    destinationAddress: string,
  ) {
    // todo: validation transaction walletAddress, price and payment.(BONK) plugin.price;
    const transaction = await this.connection.getParsedTransaction(txId, {
      commitment: 'confirmed',
      maxSupportedTransactionVersion: 0,
    });

    if (!transaction) {
      this.logger.debug(`Transaction[${txId}] not found`);
      return false;
    }

    let senderMatches = false;
    let receiverMatches = false;
    let priceMatches = false;

    // Check if sender is walletId
    const accountKeys = transaction.transaction.message.accountKeys;
    const senderAccount = accountKeys.find(
      (account) => account.pubkey.toBase58() === walletId && account.signer,
    );
    senderMatches = !!senderAccount;

    if (!senderMatches) {
      console.log(`Sender does not match: expected ${walletId}`);

      return false;
    }

    // Check if receiver is destinationAddress and price is 1000 BONK
    const instructions = transaction.transaction.message.instructions;
    const filteredInstruction = (instructions as ParsedInstruction[])
      .filter((instruction) => 'parsed' in instruction)
      .find((parsedInstruction) =>
        ['transfer', 'transferChecked'].includes(
          parsedInstruction.parsed?.type,
        ),
      );

    if (
      filteredInstruction &&
      filteredInstruction.parsed &&
      filteredInstruction.parsed.type === 'transferChecked'
    ) {
      const { destination, tokenAmount } = filteredInstruction.parsed.info;
      if (destination === destinationAddress) {
        receiverMatches = true;
      } else {
        console.log(
          `Receiver does not match: expected ${destinationAddress}, got ${destination}`,
        );

        return false;
      }

      if (tokenAmount.uiAmount === requiredAmount) {
        priceMatches = true;
      } else {
        console.log(
          `Price does not match: expected ${requiredAmount}, got ${tokenAmount.uiAmount}`,
        );

        return false;
      }
    }

    if (senderMatches && receiverMatches && priceMatches) {
      console.log('Transaction matches all criteria');
      return true;
    } else {
      console.log('Transaction does not match criteria');
      return false;
    }
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
