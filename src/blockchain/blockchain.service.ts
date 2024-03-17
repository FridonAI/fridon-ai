import { Injectable } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import {
  getDestinationAddress,
  getLatestBlockHash,
  getTokenSupply,
} from './utils/connection';
import { TokenProgramTransactionFactory } from './factories/token-program-transaction-factory';
import { TokenAmount } from './utils/token-amount';
// import { KaminoMarket } from '@hubbleprotocol/kamino-lending-sdk';

@Injectable()
export class BlockchainService {
  constructor(readonly connection: Connection) {}

  async getLatestsBlockHash(): Promise<string> {
    const res = await getLatestBlockHash(this.connection);
    return res.blockhash;
  }

  async createTokenAccount(): Promise<string> {
    return 'tokenAccount';
  }

  async transferTokens(
    from: string,
    to: string,
    mintAddress: string,
    amount: number,
  ): Promise<Uint8Array> {
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
      await TokenProgramTransactionFactory.Instance.generateTransferTransaction(
        from,
        receiver,
        mintAddress,
        amountBN,
        this.connection,
      );

    const serializedTransaction = transferTransaction.serialize();
    console.log('transferTransaction', serializedTransaction);

    return serializedTransaction;
  }

  // async getKaminoVaultInformation() {
  //   console.log('Hello, Kamino!');

  //   const market = await KaminoMarket.load(
  //     this.connection,
  //     new PublicKey('7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF'), // main market address. Defaults to 'Main' market
  //   );

  //   console.log(market);

  //   if (market == null) {
  //     throw new Error("Couldn't load market");
  //   }

  //   const { reserves } = market;

  //   const info = Object.values(reserves).map((reserve) => {
  //     const {
  //       symbol,
  //       address,
  //       stats: {
  //         decimals,
  //         mintAddress,
  //         loanToValuePct,
  //         reserveDepositLimit,
  //         reserveBorrowLimit,
  //         mintTotalSupply,
  //       },
  //     } = reserve;
  //     const totalSupply = reserve.getTotalSupply();
  //     const totalBorrows = reserve.getBorrowedAmount();
  //     const depositTvl = reserve.getDepositTvl();

  //     return {
  //       symbol,
  //       address: address.toBase58(),
  //       decimals,
  //       mintAddress,
  //       loanToValuePct,
  //       reserveDepositLimit: reserveDepositLimit
  //         .div(10 ** decimals)
  //         .toDecimalPlaces(decimals)
  //         .toString(),
  //       reserveBorrowLimit: reserveBorrowLimit
  //         .div(10 ** decimals)
  //         .toDecimalPlaces(decimals)
  //         .toString(),
  //       mintTotalSupply: mintTotalSupply.toString(),
  //       totalSupply: totalSupply
  //         .div(10 ** decimals)
  //         .toDecimalPlaces(decimals)
  //         .toString(),
  //       totalBorrows: totalBorrows
  //         .div(10 ** decimals)
  //         .toDecimalPlaces(decimals)
  //         .toString(),
  //       depositTvl,
  //     } as KaminoVaultType;
  //   });

  //   return info;
  // }
}

export type KaminoVaultType = {
  symbol: string;
  address: string;
  decimals: number;
  mintAddress: string;
  loanToValuePct: number;
  reserveDepositLimit: number;
  reserveBorrowLimit: number;
  mintTotalSupply: number;
  totalSupply: number;
  totalBorrows: number;
  depositTvl: number;
};
