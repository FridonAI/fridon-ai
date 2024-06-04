import { PublicKey } from '@metaplex-foundation/js';
import { InterfaceSnippet } from '../interface';
import { HttpException, Logger } from '@nestjs/common';
import { TokenAmount } from 'src/blockchain/utils/tools/token-amount';
import { TRANSFER_FEE } from '../shared/contants';
import { Registry } from 'src/data-providers/registry';

type Request = {
  walletAddress: string;
  currency: string;
  amount: number;
};

type Response = {
  serializedTx: number[];
};

@Registry('kamino-repay')
export class KaminoRepay extends InterfaceSnippet<Request, Response> {
  private logger = new Logger(KaminoRepay.name);

  async execute(data: Request): Promise<Response> {
    this.logger.log(`Executing action: ${KaminoRepay.name}`);

    const { walletAddress, currency, amount } = data;

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

    const tx = await this.kaminoFactory.repay(
      walletAddress,
      mintAddress,
      amount,
      this.connection,
    );

    return {
      serializedTx: Object.values(tx.serialize()),
    };
  }
}
