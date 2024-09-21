import { PublicKey } from '@metaplex-foundation/js';
import { InterfaceSnippet } from '../interface';
import { HttpException, Logger } from '@nestjs/common';
import { Connection, PublicKeyInitData } from '@solana/web3.js';
import { TokenAmount } from 'src/blockchain/utils/tools/token-amount';
import { Registry } from 'src/data-providers/registry';
import { getDestinationAddress } from './utils/domain-utils';

type Request = {
  walletAddress: string;
  toAddress: string;
  currency: string;
  amount: number;
};

type Response = {
  serializedTx: number[];
};

@Registry('wallet-transfer')
export class TransferTokens extends InterfaceSnippet<Request, Response> {
  private logger = new Logger(TransferTokens.name);

  async execute(data: Request): Promise<Response> {
    this.logger.log(`Executing action: ${TransferTokens.name}`);

    const { walletAddress: from, toAddress: to, currency, amount } = data;

    try {
      new PublicKey(from);
    } catch (error) {
      throw new HttpException('Invalid wallet address', 403);
    }

    if (amount <= 0) {
      throw new HttpException('Amount must be greater than 0', 403);
    }

    // convert symbol if needed
    const updatedCurrency = this.tools.getCurrencySymbol(currency);

    const mintAddress =
      await this.tools.convertSymbolToMintAddress(updatedCurrency);

    const tokenInfo = await this.getTokenSupply(mintAddress, this.connection);

    if (!tokenInfo) {
      throw new HttpException(`Token ${updatedCurrency} not found`, 404);
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

    // Send Transaction

    return {
      serializedTx: Object.values(serializedTransaction),
    };
  }

  private async getTokenSupply(
    mintAddress: PublicKeyInitData,
    connection: Connection,
  ) {
    const tokenInfo = await connection.getTokenSupply(
      new PublicKey(mintAddress),
    );

    return tokenInfo;
  }
}
