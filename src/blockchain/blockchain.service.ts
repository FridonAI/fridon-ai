import { Injectable } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { getDestinationAddress, getTokenSupply } from './utils/connection';
import { TokenProgramTransactionFactory } from './factories/token-program-transaction-factory';
import { TokenAmount } from './utils/tools/token-amount';
import {
  BalanceOperationType,
  BalanceProviderType,
  BalanceType,
  OperationType,
  ProviderType,
} from './utils/types';
import { KaminoFactory } from './providers/kamino-factory';
import { BlockchainTools } from './utils/tools/blockchain-tools';

@Injectable()
export class BlockchainService {
  constructor(
    private readonly connection: Connection,
    private readonly tools: BlockchainTools,
    private readonly tokenProgramTransactionFactory: TokenProgramTransactionFactory,
    private readonly kaminoFactory: KaminoFactory,
  ) {}

  async transferTokens(
    from: string,
    to: string,
    currency: string,
    amount: number,
  ): Promise<Uint8Array> {
    const mintAddress = await this.tools.convertSymbolToMintAddress(currency);

    const tokenInfo = await getTokenSupply(mintAddress, this.connection);

    if (!tokenInfo) {
      throw new Error('Token Supply not found');
    }

    const receiver = await getDestinationAddress(this.connection, to);

    if (!receiver) {
      throw new Error('Receiver not found');
    }

    const decimals = tokenInfo.value.decimals;
    const amountBN = new TokenAmount(amount, decimals, false).toWei();

    const transferTransaction =
      await this.tokenProgramTransactionFactory.generateTransferTransaction(
        from,
        receiver,
        mintAddress,
        amountBN,
        this.connection,
      );

    const serializedTransaction = transferTransaction.serialize();

    return serializedTransaction;
  }

  async balanceOperations(
    walletAddress: string,
    provider: BalanceProviderType,
    operation: BalanceOperationType,
    currency?: string | undefined,
  ): Promise<BalanceType[]> {
    const mintAddress = currency
      ? await this.tools.convertSymbolToMintAddress(currency)
      : undefined;

    if (provider == BalanceProviderType.Kamino) {
      if (operation == BalanceOperationType.Borrowed) {
        const positions = await this.kaminoFactory.getKaminoBorrows(
          walletAddress,
          mintAddress,
        );
        return await this.tools.convertPositionsToBalances(positions);
      } else if (operation == BalanceOperationType.Deposited) {
        const positions = await this.kaminoFactory.getKaminoDepositions(
          walletAddress,
          mintAddress,
        );
        return await this.tools.convertPositionsToBalances(positions);
      } else if (operation == BalanceOperationType.All) {
        const positions =
          await this.kaminoFactory.getKaminoBalances(walletAddress);
        return await this.tools.convertPositionsToBalances(positions);
      }
    }

    if (provider == BalanceProviderType.Wallet) {
      // If mint address we need exact token balance, if no lets fetch all ones?
    }

    return [];
  }

  async defiOperations(
    walletAddress: string,
    operation: OperationType,
    provider: ProviderType,
    currency: string,
    amount: number,
  ) {
    const mintAddress = await this.tools.convertSymbolToMintAddress(currency);
    const instance = this.getProviderInstance(provider);

    switch (operation) {
      case OperationType.Supply:
        return instance.supply(
          walletAddress,
          mintAddress,
          amount,
          this.connection,
        );
      case OperationType.Borrow:
        return instance.borrow(
          walletAddress,
          mintAddress,
          amount,
          this.connection,
        );
      case OperationType.Repay:
        return instance.repay(
          walletAddress,
          mintAddress,
          amount,
          this.connection,
        );
      case OperationType.Withdraw:
        return instance.withdraw(
          walletAddress,
          mintAddress,
          amount,
          this.connection,
        );
      default:
        throw new Error('Operation not supported');
    }
  }

  private getProviderInstance(provider: ProviderType) {
    switch (provider) {
      case ProviderType.Kamino:
        return this.kaminoFactory;
      default:
        throw new Error('Provider not supported');
    }
  }
}
