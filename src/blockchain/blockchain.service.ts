import { Injectable } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { getLatestBlockHash } from './utils/connection';
import { generateTransferTransaction } from './utils/transaction';

@Injectable()
export class BlockchainService {
  constructor(
    readonly connection: Connection
  ) { }

  async getLatestsBlockHash(): Promise<string> {
    const res = await getLatestBlockHash();
    return res.blockhash;
  }


  async createTokenAccount(): Promise<string> {
    return 'tokenAccount';
  }

  async transferTokens(
    from: string,
    to: string,
    mintAddress: string,
    amount: number
  ): Promise<boolean> {
    const transactionMessage = await generateTransferTransaction(
      from,
      to,
      mintAddress,
      amount,
    );

    console.log("transactionMessage", transactionMessage);

    return true;
  }
}
