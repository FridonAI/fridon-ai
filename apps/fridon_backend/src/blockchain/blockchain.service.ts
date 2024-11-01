import { HttpException, Injectable, Logger } from '@nestjs/common';
import { Connection, PublicKey } from '@solana/web3.js';
import { getDestinationAddress, getTokenSupply } from './utils/connection';
import { TokenProgramTransactionFactory } from './factories/token-program-transaction-factory';
import { TokenAmount } from './utils/tools/token-amount';
import {
  BalanceOperationType,
  BalanceProviderType,
  BalanceType,
  OperationType,
  PointsProviderType,
  ProviderType,
  SymmetryOperationType,
} from './utils/types';
import { KaminoFactory } from './providers/kamino-factory';
import { BlockchainTools } from './utils/tools/blockchain-tools';
import { WalletFactory } from './providers/wallet-factory';
import {
  SymmetryApiFactory,
  SymmetryFundsType,
} from './providers/symmetry-api-factory';
import { PointsFactory } from './providers/points-factory';
import { JupiterFactory } from './providers/jupiter-factory';
import { TRANSFER_FEE } from './utils/constants';

@Injectable()
export class BlockchainService {
  private readonly logger = new Logger(BlockchainService.name);
  constructor(
    private readonly connection: Connection,
    private readonly tools: BlockchainTools,
    private readonly tokenProgramTransactionFactory: TokenProgramTransactionFactory,
    private readonly kaminoFactory: KaminoFactory,
    private readonly walletFactory: WalletFactory,
    private readonly pointsFactory: PointsFactory,
    private readonly symmetryFactory: SymmetryApiFactory,
    private readonly jupiterFactory: JupiterFactory,
  ) {}

  async swapTokens(
    walletAddress: string,
    fromToken: string,
    toToken: string,
    amount: number,
  ) {
    this.logger.log(this.connection.rpcEndpoint);
    if (amount <= 0) {
      throw new HttpException('Amount must be greater than 0', 403);
    }

    try {
      new PublicKey(walletAddress);
    } catch (error) {
      throw new HttpException('Invalid wallet address', 403);
    }

    const accountInfo = await this.connection.getAccountInfo(
      new PublicKey(walletAddress),
    );

    if (!accountInfo) {
      throw new HttpException('Sol Account not found', 404);
    }

    const solBalance = new TokenAmount(accountInfo!.lamports, 9, true).toWei();
    if (solBalance.lt(TRANSFER_FEE)) {
      throw new HttpException(`Insufficient balance for Fees!`, 403);
    }

    const fromMintAddress = await this.tools.convertSymbolToMintAddress(
      this.tools.getCurrencySymbol(fromToken),
    );

    const toMintAddress = await this.tools.convertSymbolToMintAddress(
      this.tools.getCurrencySymbol(toToken),
    );

    const tokenBalance = await this.tools.getTokenBalanceSpl(
      this.connection,
      new PublicKey(walletAddress),
      new PublicKey(fromMintAddress),
    );

    if (parseFloat(tokenBalance.fixed()) < amount) {
      throw new HttpException('Insufficient balance', 403);
    }

    const tokenInfo = await getTokenSupply(fromMintAddress, this.connection);

    if (!tokenInfo) {
      throw new HttpException('Token not found', 404);
    }

    const decimals = tokenInfo.value.decimals;
    const amountBN = new TokenAmount(amount, decimals, false);

    return await this.jupiterFactory.swapTokens(
      walletAddress,
      fromMintAddress,
      toMintAddress,
      amountBN.toNumber(),
    );
  } // +

  async getProtocolPoints(walletAddress: string, provider: PointsProviderType) {
    return this.pointsFactory.getPoints(walletAddress, provider);
  } // +

  async getSymmetryBaskets(): Promise<SymmetryFundsType[]> {
    return await this.symmetryFactory.getAllBaskets();
  }

  async transferTokens(
    from: string,
    to: string,
    currency: string,
    amount: number,
  ): Promise<Uint8Array> {
    try {
      new PublicKey(from);
    } catch (error) {
      throw new HttpException('Invalid wallet address', 403);
    }

    if (amount <= 0) {
      throw new HttpException('Amount must be greater than 0', 403);
    }

    // convert symbol if needed
    currency = this.tools.getCurrencySymbol(currency);

    const mintAddress = await this.tools.convertSymbolToMintAddress(currency);

    const tokenInfo = await getTokenSupply(mintAddress, this.connection);

    if (!tokenInfo) {
      throw new HttpException(`Token ${currency} not found`, 404);
    }

    const receiver = await getDestinationAddress(this.connection, to);

    if (!receiver) {
      throw new HttpException('Receiver Address not found', 404);
    }

    const decimals = tokenInfo.value.decimals;
    const amountBN = new TokenAmount(amount, decimals, false).toWei();

    const tokenBalance = await this.tools.getTokenBalanceSpl(
      this.connection,
      new PublicKey(from),
      new PublicKey(mintAddress),
    );

    if (tokenBalance.toWei().toNumber() < amountBN.toNumber()) {
      throw new HttpException('Insufficient balance', 403);
    }

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
  } // +

  async balanceOperations(
    walletAddress: string,
    provider: BalanceProviderType,
    operation: BalanceOperationType,
    currency?: string | undefined,
  ): Promise<BalanceType[]> {
    try {
      new PublicKey(walletAddress);
    } catch (error) {
      throw new HttpException('Invalid wallet address', 403);
    }
    const balances: BalanceType[] = [];

    let mintAddress = currency
      ? await this.tools.convertSymbolToMintAddress(currency)
      : undefined;

    if (currency == 'all') {
      mintAddress = undefined;
    }

    if (
      provider == BalanceProviderType.Kamino ||
      provider == BalanceProviderType.All
    ) {
      if (operation == BalanceOperationType.Borrowed) {
        const positions = await this.kaminoFactory.getKaminoBorrows(
          walletAddress,
          mintAddress,
          currency,
        );
        if (positions.length == 0) {
          if (mintAddress) {
            return [
              {
                amount: '0',
                mintAddress: mintAddress,
                symbol:
                  await this.tools.convertMintAddressToSymbol(mintAddress),
                value: '0',
                type: 'Borrow',
              },
            ];
          }

          throw new HttpException('Your borrowed balance on Kamino is 0', 404);
        }

        balances.push(
          ...(await this.tools.convertPositionsToBalances(positions, 'Borrow')),
        );
      } else if (operation == BalanceOperationType.Deposited) {
        const positions = await this.kaminoFactory.getKaminoDepositions(
          walletAddress,
          mintAddress,
          currency,
        );
        if (positions.length == 0) {
          if (mintAddress) {
            return [
              {
                amount: '0',
                mintAddress: mintAddress,
                symbol:
                  await this.tools.convertMintAddressToSymbol(mintAddress),
                value: '0',
                type: 'Deposit',
              },
            ];
          }

          throw new HttpException('Your deposit balance on Kamino is 0', 404);
        }
        balances.push(
          ...(await this.tools.convertPositionsToBalances(
            positions,
            'Deposit',
          )),
        );
      } else if (operation == BalanceOperationType.All) {
        const { deposits, borrows } =
          await this.kaminoFactory.getKaminoBalances(
            walletAddress,
            mintAddress,
            currency,
          );
        if (deposits.length === 0 && borrows.length === 0) {
          if (mintAddress) {
            return [
              {
                amount: '0',
                mintAddress: mintAddress,
                symbol:
                  await this.tools.convertMintAddressToSymbol(mintAddress),
                value: '0',
              },
            ];
          }

          throw new HttpException('Your balance on Kamino is 0', 404);
        }

        balances.push(
          ...(await this.tools.convertPositionsToBalances(deposits, 'Deposit')),
          ...(await this.tools.convertPositionsToBalances(borrows, 'Borrow')),
        );
      }
    }
    if (
      provider == BalanceProviderType.Wallet ||
      provider == BalanceProviderType.All
    ) {
      // If mint address we need exact token balance, if no lets fetch all ones
      const tokenBalances = await this.walletFactory.getWalletBalances(
        walletAddress,
        await this.tools.getMintAddresses(),
        mintAddress ? [mintAddress] : [],
      );

      if (tokenBalances.length == 0) {
        if (mintAddress) {
          throw new HttpException(
            `${currency?.toUpperCase()} token account not found, you do not have this token in your wallet.`,
            404,
          );
        }

        throw new HttpException('Your Wallet balance is 0', 404);
      }

      balances.push(
        ...(await this.tools.convertTokenBalancesToBalances(tokenBalances)),
      );
    }

    if (
      provider == BalanceProviderType.Symmetry ||
      provider == BalanceProviderType.All
    ) {
      if (operation == BalanceOperationType.All) {
        balances.push(
          ...(await this.symmetryFactory.getWalletBaskets(
            walletAddress,
            this.connection.rpcEndpoint,
            mintAddress,
          )),
        );
      }
    }

    return balances;
  } // +

  async defiOperations(
    walletAddress: string,
    operation: OperationType,
    provider: ProviderType,
    currency: string,
    amount: number,
  ) {
    try {
      new PublicKey(walletAddress);
    } catch (error) {
      throw new HttpException('Invalid wallet address', 403);
    }
    const accountInfo = await this.connection.getAccountInfo(
      new PublicKey(walletAddress),
    );

    if (!accountInfo) {
      throw new HttpException('Sol Account not found', 404);
    }

    const solBalance = new TokenAmount(accountInfo!.lamports, 9, true).toWei();
    if (solBalance.lt(TRANSFER_FEE)) {
      throw new HttpException(`Insufficient balance for Fees!`, 403);
    }

    const mintAddress = await this.tools.convertSymbolToMintAddress(currency);
    const instance = this.getProviderInstance(provider);

    const tokenBalance = await this.tools.getTokenBalanceSpl(
      this.connection,
      new PublicKey(walletAddress),
      new PublicKey(mintAddress),
    );

    if (parseFloat(tokenBalance.fixed()) < amount) {
      throw new HttpException('Insufficient balance', 403);
    }

    if (amount <= 0) {
      throw new HttpException('Amount must be greater than 0', 403);
    }

    switch (operation) {
      case OperationType.Supply:
        return instance.supply(walletAddress, mintAddress, amount);
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
        throw new HttpException('Operation not supported', 403);
    }
  } // +

  async getSymmetryOperations(
    walletAddress: string,
    basketName: string,
    amount: number,
    operation: SymmetryOperationType,
  ) {
    try {
      new PublicKey(walletAddress);
    } catch (error) {
      throw new HttpException('Invalid wallet address', 403);
    }

    if (operation === SymmetryOperationType.Deposit) {
      return await this.symmetryFactory.depositBasketApi(
        walletAddress,
        basketName,
        amount,
      );
    }

    throw new HttpException('Operation not supported', 403);
  }

  private getProviderInstance(provider: ProviderType) {
    switch (provider) {
      case ProviderType.Kamino:
        return this.kaminoFactory;
      default:
        throw new HttpException('Provider not supported', 403);
    }
  }
}
