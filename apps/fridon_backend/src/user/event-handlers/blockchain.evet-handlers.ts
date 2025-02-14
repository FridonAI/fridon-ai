import { BadRequestException, Logger } from '@nestjs/common';
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
import { getAssociatedTokenAddress } from 'spl';
import { PublicKey } from '@metaplex-foundation/js';

export const PY_USD_MINT_ADDRESS =
  '2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo';
export const USDC_MINT_ADDRESS = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v';
export const SOL_MINT_ADDRESS = 'So11111111111111111111111111111111111111112';

@EventsHandler(TransactionConfirmedEvent)
export class PurchaseTransactionConfirmedHandler {
  constructor(
    private readonly pluginsService: PluginsService,
    private readonly userService: UserService,
    private readonly connection: Connection,
  ) {}

  private readonly logger = new Logger(
    PurchaseTransactionConfirmedHandler.name,
  );

  async handle(event: TransactionConfirmedEvent) {
    this.logger.debug(`Processing PaymentTransaction[${event.transactionId}]`);

    switch (event.transactionType) {
      case TransactionType.VERIFY:
        await this.handleTransactionVerified(event);
        break;
      case TransactionType.PAYMENT:
        await this.handleTransactionPayment(event);
        break;
      default:
        this.logger.debug(
          `TransactionType[${event.transactionType}] not supported`,
        );
        break;
    }
  }

  async handleTransactionVerified(event: TransactionConfirmedEvent) {
    // Todo: Verify required amount
    const requiredAmount = 0.1 * 10 ** 9;
    const destinationAddress = '7w777WfMRymWWAHiHcgNEobNgGooMBEd5uCezW539Zju';
    const txId = event.transactionId;

    console.log('Start Verify Transaction');
    await this.validateTransaction(
      event.transactionId,
      event.aux.walletId,
      requiredAmount,
      destinationAddress,
      '',
      0,
      SOL_MINT_ADDRESS,
      TransactionType.VERIFY,
    );

    console.log('Transaction Verified');

    // Make User Verified
    await this.userService.verifyUser(
      event.aux.walletId,
      txId,
      requiredAmount, // amount
    );

    console.log('User Verified');

    return true;
  }

  async handleTransactionPayment(event: TransactionConfirmedEvent) {
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
    const destinationAddress = plugin.owner;
    const creatorAddress = '7w777WfMRymWWAHiHcgNEobNgGooMBEd5uCezW539Zju';
    const requiredAmount = plugin.price * 10 ** 5;
    const creatorFee = 0.1;

    await this.validateTransaction(
      event.transactionId,
      event.aux.walletId,
      requiredAmount,
      destinationAddress,
      creatorAddress,
      creatorFee,
      PY_USD_MINT_ADDRESS,
      TransactionType.PAYMENT,
    );

    // date is now plus 3 month
    const expirationDate = new Date();
    expirationDate.setMonth(expirationDate.getMonth() + 1);

    this.logger.debug(`Plugin[${plugin.name}] found`);
    await this.userService.assignPlugin({
      walletId: event.aux.walletId,
      pluginId: plugin.slug,
      // ToDo: Calculate expiration date, default now plus 3 month
      expiresAt: expirationDate,
    });
  }

  private async validateTransaction(
    txId: string,
    walletId: string,
    requiredAmount: number,
    destinationAddress: string,
    creatorAddress: string,
    creatorFee: number,
    tokenAddress: string,
    transactionType: TransactionType,
  ) {
    // Associated Token Account addresses of bonk
    const destinationTokenAccount = await getAssociatedTokenAddress(
      new PublicKey(tokenAddress),
      new PublicKey(destinationAddress),
    );

    const creatorTokenAccount =
      transactionType === TransactionType.PAYMENT
        ? await getAssociatedTokenAddress(
            new PublicKey(tokenAddress),
            new PublicKey(creatorAddress),
          )
        : null;

    const transaction = await this.connection.getParsedTransaction(txId, {
      commitment: 'confirmed',
      maxSupportedTransactionVersion: 0,
    });

    if (!transaction) {
      this.logger.debug(`Transaction[${txId}] not found`);
      return false;
    }

    // Check if sender is walletId
    const accountKeys = transaction.transaction.message.accountKeys;
    const senderAccount = accountKeys.find(
      (account) => account.pubkey.toBase58() === walletId && account.signer,
    );

    if (!senderAccount) {
      throw new BadRequestException(
        `Sender does not match: expected ${walletId}`,
      );
    }

    const instructions = transaction.transaction.message.instructions;
    const filteredInstructions = (instructions as ParsedInstruction[])
      .filter((instruction) => 'parsed' in instruction)
      .filter((parsedInstruction) =>
        ['transfer', 'transferChecked'].includes(
          parsedInstruction.parsed?.type,
        ),
      );

    if (tokenAddress === SOL_MINT_ADDRESS) {
      const filteredInstruction = filteredInstructions[0];
      if (
        filteredInstruction &&
        filteredInstruction.parsed &&
        filteredInstruction.parsed.type === 'transfer'
      ) {
        const { destination, lamports } = filteredInstruction.parsed.info as {
          destination: string;
          lamports: number;
        };

        if (destination !== destinationAddress) {
          throw new BadRequestException(
            `Destination does not match: expected ${destinationAddress}, got ${destination}`,
          );
        }

        if (!this.isEqualNumber(lamports, requiredAmount)) {
          throw new BadRequestException(
            `Amount does not match: expected ${requiredAmount}, got ${lamports}`,
          );
        }

        return;
      }
    }

    // Validate creator and wallet price, destinations.
    for (const filteredInstruction of filteredInstructions) {
      if (
        filteredInstruction &&
        filteredInstruction.parsed &&
        filteredInstruction.parsed.type === 'transfer'
      ) {
        const { destination, amount } = filteredInstruction.parsed.info as {
          amount: string;
          authority: string;
          destination: string;
          source: string;
        };

        if (
          transactionType === TransactionType.PAYMENT &&
          creatorTokenAccount
        ) {
          if (destination === creatorTokenAccount.toBase58()) {
            const expectedAmount = requiredAmount * creatorFee;
            if (!this.isEqual(amount, expectedAmount)) {
              throw new BadRequestException(
                `Creator fee does not match: expected ${requiredAmount * creatorFee}, got ${amount}`,
              );
            }
          }
        }

        if (destination === destinationTokenAccount.toBase58()) {
          const expectedAmount = requiredAmount * (1 - creatorFee);
          if (!this.isEqual(amount, expectedAmount)) {
            throw new BadRequestException(
              `Wallet price does not match: expected ${requiredAmount * (1 - creatorFee)}, got ${amount}`,
            );
          }
        }

        if (
          // destination !== creatorTokenAccount.toBase58() &&
          destination !== destinationTokenAccount.toBase58()
        ) {
          throw new BadRequestException(
            `Destination does not match: expected ${destinationTokenAccount.toBase58()}, got ${destination}`,
          );
        }
      }
    }

    return true;
  }

  isEqual(amount: string, requiredAmount: number) {
    const lowerBound = requiredAmount * 0.99;
    const upperBound = requiredAmount * 1.01;
    return parseInt(amount) >= lowerBound && parseInt(amount) <= upperBound;
  }

  isEqualNumber(amount: number, requiredAmount: number) {
    const lowerBound = requiredAmount * 0.99;
    const upperBound = requiredAmount * 1.01;
    return amount >= lowerBound && amount <= upperBound;
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
