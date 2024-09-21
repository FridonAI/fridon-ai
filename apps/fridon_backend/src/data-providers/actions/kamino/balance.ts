import { PublicKey } from '@metaplex-foundation/js';
import { InterfaceSnippet } from '../interface';
import { HttpException, Logger } from '@nestjs/common';
import { BalanceOperationType, BalanceType } from '../shared/types';
import { Registry } from 'src/data-providers/registry';

type Request = {
  walletAddress: string;
  currency: string;
  operation: BalanceOperationType;
};

type Response = BalanceType[];

@Registry('kamino-balance')
export class KaminoBalance extends InterfaceSnippet<Request, Response> {
  private logger = new Logger(KaminoBalance.name);
  async execute(data: Request): Promise<Response> {
    this.logger.log(`Executing action: ${KaminoBalance.name}`);

    const { walletAddress, operation, currency } = data;
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
              symbol: await this.tools.convertMintAddressToSymbol(mintAddress),
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
              symbol: await this.tools.convertMintAddressToSymbol(mintAddress),
              value: '0',
              type: 'Deposit',
            },
          ];
        }

        throw new HttpException('Your deposit balance on Kamino is 0', 404);
      }
      balances.push(
        ...(await this.tools.convertPositionsToBalances(positions, 'Deposit')),
      );
    } else if (operation == BalanceOperationType.All) {
      const { deposits, borrows } = await this.kaminoFactory.getKaminoBalances(
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
              symbol: await this.tools.convertMintAddressToSymbol(mintAddress),
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

    return balances;
  }
}
