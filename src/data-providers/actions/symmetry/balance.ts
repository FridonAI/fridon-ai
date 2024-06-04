import { Registry } from 'src/data-providers/registry';
import { InterfaceSnippet } from '../interface';
import { BalanceOperationType, BalanceType } from '../shared/types';
import { PublicKey } from '@metaplex-foundation/js';
import { HttpException, Logger } from '@nestjs/common';

type Request = {
  walletAddress: string;
  currency: string;
  operation: BalanceOperationType;
};

type Response = BalanceType[];

@Registry('symmetry-balance')
export class SymmetryBalance extends InterfaceSnippet<Request, Response> {
  private logger = new Logger(SymmetryBalance.name);

  async execute(data: Request): Promise<Response> {
    this.logger.log(`Executing action: ${SymmetryBalance.name}`);

    const { walletAddress, currency } = data;

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

    balances.push(
      ...(await this.symmetryFactory.getWalletBaskets(
        walletAddress,
        this.connection.rpcEndpoint,
        mintAddress,
      )),
    );

    return balances;
  }
}
