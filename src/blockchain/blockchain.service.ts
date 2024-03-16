import { Injectable } from '@nestjs/common';
import { Connection } from '@solana/web3.js';

@Injectable()
export class BlockchainService {
  constructor(readonly connection: Connection) {}

  async getLatestsBlockHash(): Promise<string> {
    const res = await this.connection.getLatestBlockhash();
    return res.blockhash;
  }
}
